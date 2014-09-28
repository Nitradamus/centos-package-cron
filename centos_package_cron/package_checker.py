import operator

class PackageChecker:
	def __init__(self, errata_fetcher, package_fetcher, os_fetcher):
		self.errata_fetcher = errata_fetcher
		self.package_fetcher = package_fetcher
		self.os_fetcher = os_fetcher
	
	def match_advisory_against_installed(self,advisory_package,current_installed):
		return filter(lambda inst: advisory_package['name'] == inst.name and  
		(advisory_package['version'] > inst.version or
		(advisory_package['version'] == inst.version and advisory_package['release'] > inst.release)),current_installed)
	
	def findAdvisoriesOnInstalledPackages(self):
		os_version = self.os_fetcher.get_top_level_version()
		advisories = self.errata_fetcher.get_errata()
		current_installed = self.package_fetcher.fetch_installed_packages()
		results = []
		for advisory in advisories:
			installed_package_match = map(lambda advisory_package: self.match_advisory_against_installed(advisory_package,current_installed),advisory.packages)
			# Need to flatten
			installed_package_match = reduce(operator.add, installed_package_match)
			if len(installed_package_match) > 0 and (os_version in advisory.releases):
				results.append({'advisory': advisory, 'installed_packages':installed_package_match})
		return results
	