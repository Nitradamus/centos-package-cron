import os
import sys
import yum
import re

class Package:
	def __init__(self,name,version,release,arch):
		self.name = name
		self.version = version
		self.release = release
		self.arch = arch
	def __str__(self):
		return "Package %s-%s-%s" % (self.name, self.version, self.release)
	def __repr__(self):
		return self.__str__()
		
class ChangeLogParser:
	def get_log_version_num(self,version,release):
		match = re.match(r'^.*(\d+)\.el\S+\.(\d+)$', release)
		base = version + '-'
		return base + match.group(1) + '.' + match.group(2) if match else base + release
					
	def get_regex_pattern(self,name,version,release):
		ver = self.get_log_version_num(version,release)
		escaped = re.escape(ver)
		return r'.*^' + name +r'.*?(^\*.*? - ' + escaped + r'.*?)^\*.*'
	
	def get_regex(self,name,version,release):
		pattern = self.get_regex_pattern(name,version,release)
		return re.compile(pattern,re.MULTILINE | re.DOTALL)
	
	def parse(self,output,name,version,release):
		regex = self.get_regex(name,version,release)				
		match = regex.match(output)
		if match == None:
			raise Exception("Unable to parse changelog for package %s" % (name))
		return match.group(1)

class PackageFetcher:
	def __init__(self,changelog_parser):
		self.changelog_parser = changelog_parser
		self.yb = yum.YumBase()
		self.yb.setCacheDir()
	
	def fetch_installed_packages(self):		
		packages = self.yb.rpmdb.returnPackages()
		result = map(lambda x: Package(x.name,x.version,x.release, x.arch), packages)
		return result

	def get_package_updates(self):
		raw_updates = self.yb.update()
		result = map(lambda x: Package(x.name,x.version,x.release, x.arch), raw_updates)
		return result
		
	def get_package_changelog(self,name,version,release):
		# yum changelog updates bash-4.2.45-5.el7_0.4.x86_64
		raise 'write it'
		