/**
*  Flag administrators and special user group members with a letter
*  in parenthesis behind links that go into their user namespace.
*  E.g. Didym -> Didym (A)
*  @OrigDocumentation: https://commons.wikimedia.org/wiki/MediaWiki_talk:Gadget-markAdmins.js
*  @Documentation https://en.wikipedia.org/wiki/User:Mdaniels5757/markAdmins
*
*  @rev 3 (14:14, 20 August 2019 (UTC))
*  @author Euku - 2005, PDD, Littl, Guandalug
*  @author Didym - 2014
*  @author Rillke <https://blog.rillke.com> - 2014
*  @contributor Perhelion - 2017
*  @migrator Mdaniels5757 - 2020
*/
// <nowiki>
/* eslint indent:["error","tab",{"outerIIFEBody":0}] */
/* global jQuery:false, mediaWiki:false*/

(function (mw, $) {
'use strict';

var markAdmins = mw.libs.markAdmins = {
	config: {},
	defaults: {
		groups: {
			'sysop': {
				label: 'A',
				legacyName: 'admins',
				legacyLabelId: 'atxt',
				enabled: true
			},
			'oversight': {
				label: 'OS',
				legacyName: 'oversight',
				legacyLabelId: 'oversighttxt',
				enabled: true
			},
			'checkuser': {
				label: 'CU',
				legacyName: 'checkuser',
				legacyLabelId: 'checkusertxt',
				enabled: true
			},
			'bureaucrat': {
				label: 'B',
				legacyName: 'bureaucrat',
				legacyLabelId: 'bureautxt',
				enabled: true
			},
			'steward': {
				label: 'S',
				legacyName: 'steward',
				legacyLabelId: 'stewtxt',
				enabled: true
			},
			'interface-admin': {
				label: 'IA',
				legacyName: 'intadmin',
				legacyLabelId: 'iatxt'
			},
			'arbcom': {
				label: 'ARB',
				legacyName: 'arbcom',
				legacyLabelId: 'arbtxt'
			}
		},
		runOn: ['Special', 'User', 'User_talk', 'Project', 'File', 'Help'],
		runOnHistory: true,
		runOnTalk: true,
		runOnDiff: true
	},

	init: function (users) {
		markAdmins.users = users;
		// Wait for user configuration through their .js
		// Not adding as a gadget dependency because user .js
		// is sometimes invalid and fails loading and
		// gadget dependencies do not offer failed/error options
		$.when(mw.loader.using('user'), $.ready).then(markAdmins.mergeConfig, markAdmins.mergeConfig);
	},

	mergeConfig: function () {
		// Merge new configuration
		var optionsConfig = mw.user.options.get('markAdminCfg'),
			cfg = $.extend(
				true,
				markAdmins.config,
				markAdmins.defaults,
				window.markAdminCfg || {},
				optionsConfig ? JSON.parse(optionsConfig) : {}
			);

		markAdmins.ns = mw.config.get('wgNamespaceNumber');
		cfg.markSubpages = !!window.marksubpages;
		cfg.dontMarkMyself = window.dontmarkmyself ? mw.config.get('wgUserName') : false;

		// Namespace run conditions
		if (!(cfg.runOn.indexOf(mw.config.get('wgCanonicalNamespace')) !== -1 ||
			cfg.runOnHistory && mw.config.get('wgAction') === 'history' ||
			cfg.runOnTalk && markAdmins.ns % 2 ||
			cfg.runOnDiff && !!mw.util.getParamValue('diff'))) return;

		// Hook-up content loading
		mw.hook('wikipage.content').add(function ($c) { markAdmins.addLabels($c); }); // bind
	},

	destroy: function () {
		markAdmins.nodes.forEach(function (n) {
			$(n).remove();
		});
	},
	nodes: [], // for reInit

	reInit: function () {
		markAdmins.fullPageProcessed = 0;
		markAdmins.destroy();
		markAdmins.mergeConfig();
	},

	addLabels: function ($content) {
		// Right, the configuration evaluation is here
		// It might be possible to use Ajax for page
		// navigation in future.
		var cfg = this.config,
			noSubpages = !cfg.markSubpages || !!({ Prefixindex: 1, Allpages: 1 })[mw.config.get('wgCanonicalSpecialPageName')],
			isUserpage = [2, 3].indexOf(this.ns) !== -1,
			reUserpage = /^\/wiki\/User([ _]talk)?:(.+)/,
			enabledGroups = {},
			marker = {},
			previousUser,
			anchors,
			node = document.createElement('b');

		node.className = 'adminMark';

		// Filter enabled groups (Do it here and not later on each anchor)
		Object.keys(cfg.groups).forEach(function (g, grpCfg) {
			grpCfg = cfg.groups[g];
			if (grpCfg.enabled) enabledGroups[g] = grpCfg;
		});

		if (!this.fullPageProcessed) $content = mw.util.$content || $content;
		if (!$content[0]) return;

		anchors = $content[0].getElementsByTagName('a');
		// Add also the userpage link
		if (isUserpage && !this.fullPageProcessed &&
			((isUserpage = document.getElementById('ca-nstab-user')) &&
			(isUserpage = isUserpage.getElementsByTagName('a')))) {
			anchors = Array.from(anchors);
			anchors.push(isUserpage[0]);
		}
		this.fullPageProcessed = true;

		if (cfg.dontMarkMyself) marker[cfg.dontMarkMyself] = '';

		for (var i = 0, len = anchors.length; i < len; ++i) {
			var a = anchors[i],
				m = a.getAttribute('href');

			if (!m) continue;
			// Extract user page ( /wiki/User_talk:Foo/subpage -> Foo/subpage )
			m = m.match(reUserpage);
			if (!m || !m[2]) continue;
			// Extract user
			var userM = m[2],
				user = userM.replace(/[/#].*/, ''),
				isMainUserpageLink = user === userM;
			
			user = decodeURIComponent(user);
			// Two consecutive links to the same user? Don't mark followups!
			previousUser = previousUser === user && !!m[1]; // isUsertalkLink
			if (previousUser) continue; // only once

			userM = marker[user];
			if (userM === undefined) {
				userM = '';
				// User groups of selected user, polish user name
				m = this.users[user.replace(/_/g, ' ')];
				if (!m) continue;

				for (var g = 0; g < m.length; g++) {
					var grpCfg = enabledGroups[m[g]];
					if (!grpCfg) continue;
					// String concatenation is oftentimes faster in modern browsers,
					// so using Arrays and joining them finally seems advantage.
					// But we would need an additional IF, so there is no gain.
					if (userM) userM += '/';
					userM += grpCfg.label;
				}
				marker[user] = userM ? [userM] : userM;
			}
			// Are there markers at all?
			if (!userM) continue;
			// Don't mark certain pages, except link to user main page.
			// Does the link go to the main user page or, if linking subpages is enabled,
			// is it not a page that is just listing subpages?
			if (!isMainUserpageLink && noSubpages) continue;
			// Check finished, now append node
			marker[user][1] = this.markUser(marker[user], a, node);
			// Required for consecutive user link check
			previousUser = user;
		} // end loop
	},

	markUser: function (mark, a, node) {
		if (mark[1]) {
			node = mark[1].cloneNode(1);
		} else {
			node = node.cloneNode(1);
			node.appendChild(document.createTextNode('\u00A0(' + mark[0] + ')'));
		}
		a.appendChild(node);
		this.nodes.push(node); // for reInit
		return node;
	}

};

mw.hook('userjs.script-loaded.markadmins').add(markAdmins.init);

}(mediaWiki, jQuery));
