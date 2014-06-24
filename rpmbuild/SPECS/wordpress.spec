%{!?_pkgdocdir: %global _pkgdocdir %{_docdir}/%{name}-%{version}}
%global wp_content %{_datadir}/wordpress/wp-content

%if 0%{?rhel} == 5
%global with_cacert 0
%else
%global with_cacert 1
%endif

Summary:    Blog tool and publishing platform
URL:        http://www.wordpress.org
Name:       wordpress
Version:    4.0
Group:      Applications/Publishing
Release:    %{build_number}.%{git_commit_hash}
License:    GPLv2
Packager:   Tom Hill <tom@clockworkcubed.com>

Source0:    %{name}-%{version}.tar.gz
Source1:    wordpress-httpd-conf
Source2:    README.fedora.wordpress

# Move wp-content to /var/www/wordpress/
# This patch doesn’t work well, see bugzilla.redhat.com/522897
Patch1: wordpress-move-wp-content.patch
# Drop swfupload: not built from source, not reasonably possible to do
Patch2: wordpress-3.9-no_swfupload.patch
# Adjust tinymce's media plugin not to use its SWF plugin. This changes
# 'p.getParam("flash_video_player_url",u.convertUrl(u.url+"/moxieplayer.swf"))'
# to 'false'
Patch3: wordpress-3.9-tinymce_noflash.patch
# Adjust mediaelement not to use its SWF and Silverlight plugins. This
# changes 'plugins:["flash,"silverlight","youtube","vimeo"]' to
# 'plugins:["youtube","vimeo"]'
Patch4: wordpress-3.9-mediaelement-noflash_silverlight.patch
# RPM configuration:
# Path to installation
# Disable auto-updater
Patch5: wordpress-3.8.1-config.patch
# RPM are readonly
# disable version check and updated
# change DISALLOW_FILE_MODS default value to true
# ignore WP_AUTO_UPDATE_CORE (always false)
Patch6: wordpress-3.9-noupdate.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

%if 0%{?rhel} == 5
Requires: php53 >= 5.2.4
Requires: php53-simplepie >= 1.3.1
%else
Requires: php >= 5.2.4
Requires: php-simplepie >= 1.3.1
%endif
# From phpcompatinfo report for version 3.8
Requires: php-curl
Requires: php-date
Requires: php-dom
Requires: php-enchant
Requires: php-ereg
Requires: php-exif
Requires: php-fileinfo
Requires: php-ftp
Requires: php-gd
Requires: php-gettext
Requires: php-hash
Requires: php-iconv
Requires: php-json
Requires: php-libxml
Requires: php-mbstring
Requires: php-mysql
Requires: php-openssl
Requires: php-pcre
Requires: php-posix
Requires: php-simplexml
Requires: php-sockets
Requires: php-spl
Requires: php-tokenizer
Requires: php-xml
Requires: php-zip
Requires: php-zlib
# Unbundled libraries
Requires: php-PHPMailer
Requires: webserver
%if %{with_cacert}
Requires: ca-certificates
%endif
Provides: wordpress-mu = %{version}-%{release}
Obsoletes: wordpress-mu < 2.9.3

%description
Wordpress is an online publishing / weblog package that makes it very easy,
almost trivial, to get information out to people on the web.

Important information in %{_pkgdocdir}/README.fedora


%prep
%setup -q -n src

# Drop pre-compiled binary lumps: Flash and Silverlight
# This means that Flash video fallbacks in Wordpress' media support
# and the tinymce plugin, the plupload Flash and Silverlight
# uploaders, and swfupload are not available.
# To re-introduce these they would have to be built from the
# ActionScript source as part of this package build, they cannot be
# shipped pre-compiled. Removing plupload.flash.js and
# plupload.silverlight.js causes plupload only to try and use the html4
# or html5 uploaders; if you just wipe the binaries but leave the
# .js files, it will try and use the Flash or Silverlight uploaders
# and draw a non-functional button. - AdamW, 2013/08
# https://fedoraproject.org/wiki/Packaging:Guidelines#No_inclusion_of_pre-built_binaries_or_libraries

rm wp-includes/js/mediaelement/silverlightmediaelement.xap
rm wp-includes/js/mediaelement/flashmediaelement.swf
rm wp-includes/js/tinymce/plugins/media/moxieplayer.swf
rm wp-includes/js/plupload/plupload.silverlight.xap
rm wp-includes/js/plupload/plupload.flash.swf

# swfupload can just die in its entirety
rm -rf wp-includes/js/swfupload

#patch0 -p1 -b .dolly
#patch1 -p1 -b .rhbz522897
%patch2 -p1
%patch3 -p1
%patch4 -p1

# We patch a .js file, used patched file instead of unpatch minified one
ln -sf plugin.js wp-includes/js/tinymce/plugins/media/plugin.min.js

# Re-Generated the archive
arc=wp-includes/js/tinymce/wp-tinymce.js
gunzip -dc $arc.gz | \
  grep "^// Source" | \
  while read a b c
do
  if [ -f $c ]; then
    echo -e "\n$a $b $c"
    cat $c
  else
    exit 1
  fi
done >$arc
gzip --force $arc
ls -l $arc.gz

# Create RPM configuration
cp wp-config-sample.php wp-config.php
%patch5 -p1
%patch6 -p1

# fix file encoding
sed -i -e 's/\r//' license.txt


%build

%install
# Apache configuration
install -m 0644 -D -p %{SOURCE1} ${RPM_BUILD_ROOT}%{_sysconfdir}/httpd/conf.d/wordpress.conf

# Application
mkdir -p ${RPM_BUILD_ROOT}%{_datadir}/wordpress
cp -pr * ${RPM_BUILD_ROOT}%{_datadir}/wordpress

# Configuration
install -m 0644 -D wp-config.php ${RPM_BUILD_ROOT}%{_sysconfdir}/wordpress/wp-config.php
/bin/ln -sf ../../../etc/wordpress/wp-config.php ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-config.php

/bin/cp %{SOURCE2} ./README.fedora

# Create additional wp-content directories so we can own them
install -d ${RPM_BUILD_ROOT}%{wp_content}/{plugins,themes,upgrade,uploads}

# Remove empty files to make rpmlint happy
find ${RPM_BUILD_ROOT} -type f -empty -exec rm -vf {} \;
# These are docs, remove them from here, docify them later
rm -f ${RPM_BUILD_ROOT}%{_datadir}/wordpress/{license.txt,readme.html}

# Remove bundled php-simplepie and link to system copy
rm     ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/class-simplepie.php
rm -rf ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/SimplePie
%if 0%{?rhel} == 5
ln -sf /usr/share/php/php53-simplepie/autoloader.php \
%else
ln -sf /usr/share/php/php-simplepie/autoloader.php \
%endif
       ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/class-simplepie.php

# Remove bundled PHPMailer and link to system one
# Note POP3 is not from PHPMailer but from SquirrelMail
for fic in phpmailer smtp; do
  rm     ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/class-$fic.php
  ln -sf /usr/share/php/PHPMailer/class.$fic.php \
         ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/class-$fic.php
done

# Remove bundled ca-bundle.crt
%if %{with_cacert}
rm ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/certificates/ca-bundle.crt
ln -s /etc/pki/tls/certs/ca-bundle.crt \
   ${RPM_BUILD_ROOT}%{_datadir}/wordpress/wp-includes/certificates/ca-bundle.crt
%endif

# Remove backup copies of patches
find ${RPM_BUILD_ROOT} \( -name \*.dolly -o -name \*.rhbz522897 -o -name \*.orig \) \
    -print -delete

## Move wp-content directory to /var/www location
#mkdir -p ${RPM_BUILD_ROOT}%{_localstatedir}/www/wordpress
#mv -v ${RPM_BUILD_ROOT}%{wp_content}/ \
#  ${RPM_BUILD_ROOT}%{_localstatedir}/www/wordpress

#%post
#if [ $1 -eq 2 ] ; then
## In case user has old wp-content from previous version, move it to
## the new location.
#mv -uf %{wp_content}/* %{_localstatedir}/www/wordpress/
#/sbin/restorecon -R %{_localstatedir}/www/wordpress/
#fi

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/wordpress.conf
%dir %{_datadir}/wordpress
%{_datadir}/wordpress/wp-admin
%{_datadir}/wordpress/wp-includes
%{_datadir}/wordpress/index.php
%dir %{wp_content}/
%{wp_content}/index.php
%dir %attr(0775,apache,ftp) %{wp_content}/plugins
%dir %attr(0775,apache,ftp) %{wp_content}/themes
%dir %attr(0775,apache,ftp) %{wp_content}/upgrade
%dir %attr(0775,apache,ftp) %{wp_content}/uploads
%{wp_content}/plugins/*
%{wp_content}/themes/*
%doc license.txt
%doc readme.html
%doc README.fedora
%{_datadir}/wordpress/wp-*.php
%config(noreplace) %{_sysconfdir}/wordpress/wp-config.php
%{_datadir}/wordpress/xmlrpc.php
%dir %{_sysconfdir}/wordpress

%changelog
* Tue Jun 24 2014 Tom Hill <tom@clockworkcubed.com> - 4.0-1
- Updated version
- Prep for jenkins
* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.9.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May  9 2014 Remi Collet <remi@fedoraproject.org> - 3.9.1-1
- update to 3.9.1 Maintenance Release

* Wed May  7 2014 Remi Collet <remi@fedoraproject.org> - 3.9-1
- update to 3.9 “Smith”

* Tue Apr 15 2014 Remi Collet <remi@fedoraproject.org> - 3.8.3-1
- update to 3.8.3 Maintenance Release
  http://wordpress.org/news/2014/04/wordpress-3-8-3/

* Wed Apr  9 2014 Remi Collet <remi@fedoraproject.org> - 3.8.2-1
- update to 3.8.2 Security Release
- fix privilege escalation issue  CVE-2014-0165
- fix authentication bypass issue CVE-2014-0166

* Sat Jan 25 2014 Remi Collet <remi@fedoraproject.org> - 3.8.1-3
- ignore WP_AUTO_UPDATE_CORE (always false)

* Fri Jan 24 2014 Remi Collet <remi@fedoraproject.org> - 3.8.1-2
- comment provided configuration about auto-updater
- disable auto-updater on default configuration #1057521
- switch some sed to patch (more robust)

* Thu Jan 23 2014 Adam Williamson <awilliam@redhat.com> - 3.8.1-1
- new upstream release 3.8.1 (bugfixes)

* Mon Dec 16 2013 Remi Collet <rcollet@redhat.com> - 3.8-1
- update to 3.8 “Parker” #1043104
- link to README.fedora in package description
- add note about optional packages #1037516
- add php dependencies: ereg, ftp, gd, xml
- del php dependencies: pdo, reflection

* Wed Oct 30 2013 Remi Collet <rcollet@redhat.com> - 3.7.1-1
- update to 3.7.1 (bugfixes)

* Fri Oct 25 2013 Remi Collet <rcollet@redhat.com> - 3.7-1
- update to 3.7
- requires ca-certificates for ca-bundle.crt

* Thu Sep 12 2013 Paul Wouters <pwouters@redhat.com> - 3.6.1-1
- update to 3.6.1, various bugs and security fixes:
  CVE-2013-4338 CVE-2013-4339 CVE-2013-4340

* Thu Aug 22 2013 Adam Williamson <awilliam@redhat.com> - 3.6.0-1
- update to 3.6.0
- drop pre-compiled Flash and Silverlight binaries - #1000267

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jun 24 2013 Remi Collet <rcollet@redhat.com> - 3.5.2-1
- version 3.5.2, various bug and security fixes:
  CVE-2013-2173 CVE-2013-2199 CVE-2013-2200 CVE-2013-2201
  CVE-2013-2202 CVE-2013-2203 CVE-2013-2204

* Tue Feb 12 2013 Remi Collet <rcollet@redhat.com> - 3.5.1-2
- provides POP3 class #905867
  POP3 is not from PHPMailer, but from SquirrelMail

* Wed Jan 30 2013 Remi Collet <rcollet@redhat.com> - 3.5.1-1.1
- fix simplepie links (for all branches)

* Wed Jan 30 2013 Remi Collet <rcollet@redhat.com> - 3.5.1-1
- version 3.5.1, various bug and security fixes:
  CVE-2013-0235, CVE-2013-0236 and CVE-2013-0237
- drop -f option from rm to break build if
  upstream archive content change
- protect akismet content (from upstream .htaccess)

* Wed Jan  2 2013 Remi Collet <rcollet@redhat.com> - 3.5-3
- fix links to system PHPMailer library

* Sun Dec 16 2012 Remi Collet <rcollet@redhat.com> - 3.5-2
- fix use of system Simplepie
- give access from local (httpd 2.4)

* Wed Dec 12 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-1
- New upstream release.

* Tue Dec 04 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-0.5.RC3
- New upstream release candidate.

* Fri Nov 30 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-0.5.RC2
- New upstream release candidate.

* Sat Nov 24 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-0.5.RC1
- New upstream release candidate.

* Tue Nov 13 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-0.4.beta3
- New upstream beta3 version

* Mon Oct 29 2012 Remi Collet <rcollet@redhat.com> - 3.5-0.3.beta2
- use system PHPMailer
- requires needed php extensions

* Sat Oct 13 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-0.2.beta2
- New upstream beta2 version

* Thu Oct 04 2012 Matěj Cepl <mcepl@redhat.com> - 3.5-0.2.beta1
- New upstream beta1 version
- Don’t even bother with removing gettext.php ... it is not used anymore

* Thu Sep 06 2012 Matej Cepl <mcepl@redhat.com> - 3.4.2-2
- Upstream security update.

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jun 28 2012 Matej Cepl <mcepl@redhat.com> - 3.4.1-1
- New upstream release. Just improvements and security issues.

* Wed Jun 13 2012 Matej Cepl <mcepl@redhat.com> - 3.4-1
- New upstream release. The main changes from the upstream
  release notes:
  * theme customizer
  * XML-RPC themes and API improvements

* Tue Jun 12 2012 Matej Cepl <mcepl@redhat.com> - 3.4-0.2.RC3
- They still haven’t released.

* Thu Jun 07 2012 Matej Cepl <mcepl@redhat.com> - 3.4-0.2.RC2
- And yet another release candidate.

* Wed May 30 2012 Matej Cepl <mcepl@redhat.com> - 3.4-0.2.RC1
- We have a release candidate now.

* Thu May 03 2012 'Matej Cepl <mcepl@redhat.com>' - 3.4-0.2.beta4
- New week, new upstream beta. Less drama than last time.

* Mon Apr 23 2012 'Matěj Cepl <mcepl@redhat.com>' - 3.4-0.2.beta3
- And yet another upstream beta (fixes CVE-2011-0700 and
  CVE-2011-0701)

* Mon Apr 16 2012 Matěj Cepl <mcepl@redhat.com> - 3.4-0.2.beta2
- And yet another upstream beta

* Thu Apr 05 2012 'Matej Cepl <mcepl@redhat.com>' - 3.4-0.1.beta1
- New upstream beta release (just for Rawhide, to be sure we build)

* Wed Jan 04 2012 'Matej Cepl <mcepl@redhat.com>' - 3.3.1-1
- Security (XSS) and maintenance upstream release.

* Tue Dec 13 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-1
- New upstream release.

* Wed Dec 07 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-0.5.RC2
- ... and one day after I upgraded to RC1, we have new RC2 ;)

* Tue Dec 06 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-0.4.RC1
- Cool we are on RC1!

* Thu Nov 24 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-0.3.beta4
- Another upstream beta release (now hopefully, really close to RC)

* Fri Nov 11 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-0.3.beta3
- Fix version requirement for php (Closes #753192)

* Wed Nov 09 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-0.2.beta3
- Another upstream beta release.

* Thu Oct 20 2011 'Matěj Cepl <mcepl@redhat.com>' - 3.3-0.1.beta2
- New upstream beta release (just for Rawhide, to be sure we build)

* Sat Jul 30 2011 Matěj Cepl <mcepl@redhat.com> - 3.2.1-2
- Rebuilt against new libraries.

* Wed Jul 13 2011 Matěj Cepl <mcepl@redhat.com> - 3.2.1-1
- New upstream release. Small fixes missed in 3.2.

* Tue Jul 05 2011 Matěj Cepl <mcepl@redhat.com> - 3.2-1
- New upstream release.

* Wed Jun 29 2011 Matěj Cepl <mcepl@redhat.com> - 3.2-0.1.RC3
- Updated prerelease version (security and minor fixes).

* Sun Jun 19 2011 Matěj Cepl <mcepl@redhat.com> - 3.2-0.1.RC1
- Prerelease version.

* Thu Jun 02 2011 Matěj Cepl <mcepl@redhat.com> - 3.1.3-3
- Actually, we just don't need gettext.php at all, it is provided by
  php itself. Just remove the file, don't make a symlink.
- revert back to wp-content in /usr/share/wordpress, I am not able to make it
  work. Not fixing BZ 522897.

* Wed Jun 01 2011 Matěj Cepl <mcepl@redhat.com> - 3.1.3-2
- Fix old FSF address and Summary to make rpmlint happy.
- Make wp-content directory owned by apache:apache
- Correctly Provides/Obsoletes (with versions)

* Wed May 25 2011 Matěj Cepl <mcepl@redhat.com> - 3.1.3-1
- Upgrade to the latest upstream version (security fixes and enhancements, BZ 707772)
- Move wp-content directory to /var/www/wordpress/ (BZ 522897)
- Simplify overly detailed %%files

* Sun May 01 2011 Matěj Cepl <mcepl@redhat.com> - 3.1.2-1
- New upstream release.

* Tue Apr 12 2011 Matěj Cepl <mcepl@redhat.com> - 3.1.1-1
- 3.1.1

* Wed Feb 23 2011 Jon Ciesla <limb@jcomserv.net> - 3.1-1
- 3.1.

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 03 2011 Jon Ciesla <limb@jcomserv.net> - 3.0.4-2
- Obsoletes wordpress-mu, deprecated by upstream as of 3.0.x.

* Mon Jan 03 2011 Jon Ciesla <limb@jcomserv.net> - 3.0.4-1
- 3.0.4. Security fixes, BZ 666782.

* Thu Dec 23 2010 Jon Ciesla <limb@jcomserv.net> - 3.0.3-2
- Change Requires from httpd to webserver, BZ 523480.
- Patch for Hello Dolly lyrics, BZ 663966.

* Fri Dec 10 2010 Jon Ciesla <limb@jcomserv.net> - 3.0.3-1
- 3.0.3. Security fixes, BZ 659319.

* Fri Dec 10 2010 Jon Ciesla <limb@jcomserv.net> - 3.0.2-1
- 3.0.2. Security fixes, BZ 659319.

* Mon Aug 09 2010 Jon Ciesla <limb@jcomserv.net> - 3.0.1-1
- 3.0.1.

* Mon Jul 12 2010 Jon Ciesla <limb@jcomserv.net> - 2.8.6-3
- Remove bundled php-gettext and php-simplepie,
- require and link to system versions, BZ 544720.

* Mon Nov 16 2009 Adrian Reber <adrian@lisas.de> - 2.8.6-2
- updated to 2.8.6 (Security Release)

* Wed Oct 21 2009 Adrian Reber <adrian@lisas.de> - 2.8.5-1
- updated to 2.8.5 (Hardening Release)

* Sun Aug 30 2009 Adrian Reber <adrian@lisas.de> - 2.8.4-1
- updated to 2.8.4 (security fixes were already available with 2.8.3-2)

* Tue Aug 11 2009 Adrian Reber <adrian@lisas.de> - 2.8.3-2
- another security update to fix "Remote admin reset password":
  http://lists.grok.org.uk/pipermail/full-disclosure/2009-August/070137.html

* Mon Aug 03 2009 Adrian Reber <adrian@lisas.de> - 2.8.3-1
- updated to 2.8.3 for security fixes

* Tue Jul 28 2009 Adrian Reber <adrian@lisas.de> - 2.8.2-1
- updated to 2.8.2 for security fixes - BZ 512900
- fixed "wrong-script-end-of-line-encoding" of license.txt
- correctly disable auto update check
- fixed an error message from 'find' during the build

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.8.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 10 2009 Adrian Reber <adrian@lisas.de> - 2.8.1-1
- updated to 2.8.1 for security fixes - BZ 510745

* Mon Jun 22 2009 Adrian Reber <adrian@lisas.de> - 2.8-1
- updated to 2.8

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 11 2009 Adrian Reber <adrian@lisas.de> - 2.7.1-1
- updated to 2.7.1

* Wed Nov 26 2008 Adrian Reber <adrian@lisas.de> - 2.6.5-2
- updated to 2.6.5

* Fri Oct 24 2008 Adrian Reber <adrian@lisas.de> - 2.6.3-1
- updated to 2.6.3

* Tue Sep 09 2008 Adrian Reber <adrian@lisas.de> - 2.6.2-1
- updated to 2.6.2

* Sun Aug 24 2008 Adrian Reber <adrian@lisas.de> - 2.6.1-1
- updated to 2.6.1

* Mon Jul 21 2008 Adrian Reber <adrian@lisas.de> - 2.6-1
- updated to 2.6

* Sat Apr 26 2008 Adrian Reber <adrian@lisas.de> - 2.5.1-1
- updated to 2.5.1 for security fixes - BZ 444396

* Fri Feb  8 2008 John Berninger <john at ncphotography dot com> - 2.3.3-0
- update to 2.3.3 for security fixes - BZ 431547

* Sun Dec 30 2007 Adrian Reber <adrian@lisas.de> - 2.3.2-1
- updated to 2.3.2 (bz 426431, Draft Information Disclosure)

* Tue Oct 30 2007 Adrian Reber <adrian@lisas.de> - 2.3.1-1
- updated to 2.3.1 (bz 357731, wordpress XSS issue)

* Mon Oct 15 2007 Adrian Reber <adrian@lisas.de> - 2.3-1
- updated to 2.3
- disabled wordpress-core-update

* Tue Sep 11 2007 Adrian Reber <adrian@lisas.de> - 2.2.3-0
- updated to 2.2.3 (security release)

* Wed Aug 29 2007 John Berninger <john at ncphotography dot com> - 2.2.2-0
- update to upstream 2.2.2
- license tag update

* Mon Apr 16 2007 john Berninger <jwb at redhat dot com> - 2.1.3-1
- update to 2.1.3 final - bz235912

* Mon Mar 26 2007 John Berninger <jwb at redhat dot com> - 2.1.3-rc2
- update to 2.1.3rc2 for bz 233703

* Sat Mar  3 2007 John Berninger <jwb at redhat dot com> - 2.1.2-0
- update to 2.1.2 - backdoor exploit introduced upstream in 2.1.1 - bz 230825

* Tue Feb 27 2007 John Berninger <jwb at redhat dot com> - 2.1.1-0
- update to 2.1.1 to fix vuln in bz 229991

* Wed Jan 31 2007 John Berninger <jwb at redhat dot com> - 2.1-0
- update to v2.1 to fix multiple bz/vuln's

* Sun Dec  3 2006 John Berninger <jwb at redhat dot com> - 2.0.5-2
- Remove mysql-server dependency

* Sun Dec  3 2006 John Berninger <jwb at redhat dot com> - 2.0.5-1
- Update to upstream 2.0.5 to fix vuln in bz 213985

* Thu Oct 26 2006 John Berninger <jwb at redhat dot com> - 2.0.4-1
- Doc fix for BZ 207822

* Sat Aug 12 2006 John Berninger <jwb at redhat dot com> - 2.0.4-0
- Upstream security vulns - bz 201989

* Sun Jul 23 2006 John Berninger <jwb at redhat dot com> - 2.0.3-4
- Fix broken upgrade path from FE4

* Tue Jul  4 2006 John Berninger <jwb at redhat dot com> - 2.0.3-3
- Add a README.fedora file
- Add php-mysql requires

* Tue Jun 20 2006 John Berninger <jwb at redhat dot com> - 2.0.3-2
- Remove use of installprefix macro
- %%{_datadir}/wordpress/wp-config.php is not a config file
- Symlink is relative

* Mon Jun 19 2006 John Berninger <jwb at redhat dot com> - 2.0.3-1
- Changes from Jarod Wilson as below
- Update to 2.0.3
- Rearrange to use /usr/share/wordpress and /etc/wordpress
- Remove patch (included upstream)
- Remove empty files to make rpmlint happy

* Tue May 30 2006 John Berninger <jwb at redhat dot com> - 2.0.2-1
- Added patch for \n cache injection - upstream changeset #3797

* Sat May 27 2006 John Berninger <jwb at redhat dot com> - 2.0.2-0
- Initial build
