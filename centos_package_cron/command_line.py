import package_checker
import package_fetcher
import errata_fetcher
import os_version_fetcher
import mockable_execute
import argparse
import socket
import sys

__VERSION__ = '1.0'

def main():
	args = parse_args()
	executor = mockable_execute.MockableExecute()
	pkg_fetcher = package_fetcher.PackageFetcher(package_fetcher.ChangeLogParser(),executor)
	checker = package_checker.PackageChecker(errata_fetcher.ErrataFetcher(),pkg_fetcher,os_version_fetcher.OsVersionFetcher())

	send_email = False
	security_advisories = list(filter(lambda adv:adv['advisory'].type == errata_fetcher.ErrataType.SecurityAdvisory,checker.findAdvisoriesOnInstalledPackages()))
	if len(security_advisories) > 0:
		send_email = True
	
	general_updates = pkg_fetcher.get_package_updates()
	changelogs = []
	if len(general_updates) > 0:
		send_email = True
		changelogs = map(lambda pkg: { 'name': pkg.name, 'changelog': pkg_fetcher.get_package_changelog(pkg.name,pkg.version,pkg.release)},general_updates)
	
	if send_email == True:
		email_content = 'The following security advisories exist for installed packages:\n\n'
		for advisory_and_package in security_advisories:
			advisory = advisory_and_package['advisory']
			associated_package_labels = map(lambda pkg: "%s-%s-%s" % (pkg.name, pkg.version, pkg.release),advisory_and_package['installed_packages'])
			severity_label = errata_fetcher.ErrataSeverity.get_label(advisory.severity)
			email_content += "Advisory ID: %s Severity: %s Packages: %s\n" % (advisory.advisory_id, severity_label, associated_package_labels)
		email_content += "\n\n"
		for update in general_updates:
			changelog_entry = next(cl for cl in changelogs if cl['name'] == update.name)			
			email_content += "Updated package %s version %s release %s, change log:\n%s\n\n" % (update.name, update.version, update.release, changelog_entry['changelog'])
		
		executor.run_command(['/usr/bin/mail',
							  '-s %s' % (args.email_subject),
							  '-r %s' % (args.email_from),
							  args.email_to],
							 email_content)
							
def parse_args():
	parser = argparse.ArgumentParser(description="Emails administrators with CentOS security updates and changelogs of non-security updates. Version %s" % __VERSION__)
	
	parser.add_argument('-e', '--email_to',
	type=str,
	required=True,
	help='Email following user with the output.'
	'Could be `centos_package_cron -e johndoe@mail.com`. '
	"Uses system's `mail` to send emails.")
	
	default_from = "CentOS Update Check on %s <noreply@centos.org>" %(socket.gethostname())
	parser.add_argument('-f', '--email_from',
	type=str,
	default=default_from,
	help='Email from this user'
	'Could be `centos_package_cron -f johndoe@mail.com`. '
	"Uses system's `mail` to send emails  Will use '%s' by default." % (default_from))
	
	default_subject= "CentOS Update Check on %s" %(socket.gethostname())
	parser.add_argument('-s', '--email_subject',
	type=str,
	default=default_subject,
	help='Email using this subject'
	'Could be `centos_package_cron -s "the test subject"`. '
	"Uses system's `mail` to send emails with this subject  Will use '%s' by default." % (default_subject))
	return parser.parse_args()

if __name__ == '__main__':
    sys.exit(main())