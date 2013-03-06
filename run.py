#!/usr/bin/python
"""
Copyright (c) 2013, SMART Technologies ULC 
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
á Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
á Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
á Neither the name of the Copyright holder (SMART Technologies ULC) nor the names of its contributors (Joshua Henn) may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER (SMART Technologies ULC) "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Purpose: Executes a test file using Jython or RobotFramework based on the file extension.  Platform independent.
"""
import re
import string

try:
	import argparse
except ImportError:
	print "Fatal Error: argparse module is missing!"
	print "Type> sudo easy_install argparse"

import getopt, sys, os, subprocess, platform
from subprocess import CalledProcessError
from sys import argv, stdout


class Target(object):
	""" Process target superclass """

	delimiter = None
	debug = False
	arguments = []
	absolutePostProcessingPath = False

	def __init__(self):
		self.delimiter = ':' if os.name == 'posix' else ';' # Windows/Unix delimiters
	
	def getBinary(self):
		
		# Support for env var specifying location of java interpreter we're suppose to use 				
		# Sikuli libs only compatible with JRE1.6 32-bit				
		return ['java']
		
	
	def getType(self):
	
		return self.__class__.__name__
	
	def getClassPath(self):
		
		return 'java/' + target.__class__.__name__.lower() + '.jar' + self.delimiter + 'java/*' + self.delimiter + '.'
	
	def getMainClass(self):	
		raise Exception("must be overridden")

	def getArgs(self):	
		raise Exception("must be overridden")
	
	def setArgs(self, args):
		self.arguments = args

	def postProcessing(self):	
		print "----------------------------"
		print "Performing post processing.."
		print "----------------------------"
		
		self.postProcessingTemplate()
		
		print "Done."
		
	def getDelimiter(self):	
		return self.delimiter
		
	def getArchitecture(self):
		return ['-d32']
		
	def getMemoryLimit(self):
		return ['-Xmx1024M']
	
	def setDebug(self, state):
		self.debug = state

	def getLogLevel(self):
		return 'TRACE'
	
		# Logging refactoring, due to limitations in RobotFramework we always want it set to trace.
		# Logging level will be set by internal mechinisms rather than using log levels
		#return 'INFO' if not self.debug else 'TRACE'
	
	def postProcessingTemplate(self):	
		pass
	
	def getRunInBackgroundPrefix(self):
		return "start"
	
	def getLaunchArgs(self):
		
		return self.getBinary() + \
				['-cp', target.getClassPath()] + \
				['-Dpython.path=.' + target.getDelimiter() + 'java/sikuli-script.jar/Lib'] + \
				self.getMemoryLimit() + \
				self.getMainClass() + \
				self.getArgs()

	def setUseAbsolutePostProcessingPath(self, boolean):
		self.absolutePostProcessingPath = boolean
		

class RobotFramework(Target):
		
	def getMainClass(self):		
		return ["org.robotframework.RobotFramework"]
		
	def getArgs(self):	
		
		return ['--pythonpath=.', \
				'--outputdir=results', \
				'--loglevel=' + self.getLogLevel(), \
				'--name', '"Product"'] + self.arguments + [ args.target ]
	
	def postProcessingTemplate(self):

		absoluteArgument = ['--absolute'] if self.absolutePostProcessingPath else [] 
	
		# Markup the log.html file
		subprocess.call(['python', 'tools/sikulifw/patchLog.py', 'results/log.html'] + absoluteArgument)
		
		# Create NUnit XML
		subprocess.call(['python', 'tools/sikulifw/robotXMLConverter.py', 'n', 'results/output.xml', 'results/nunit.xml'])


class Python(Target):
	
	def getBinary(self):
		return ['python']
	
	def getArgs(self):	
		
		return [args.target] + self.arguments
	
	def getLaunchArgs(self):
		
		return self.getBinary() + \
				self.getArgs()			
		

class Jython(Target):

	def getMainClass(self):	
		return ["org.python.util.jython"]
		
	def getArgs(self):	
		return ['-Dpythonpath=.',
				'-Dloglevel=' + self.getLogLevel(),
				args.target ] + self.arguments		
	
class TargetFactory(object):

	@classmethod
	def getTarget(cls, filename):
				
		# Check what type of file we're trying to execute
		if filename[-3:] == '.py':
			
			# Parse the python file and look for an "Interpreter: <interp>" line 
			f = open(filename)
			match = re.search("Interpreter(?:.{1,5})(python|jython)",f.read() , re.IGNORECASE)
			if match:
				if str.lower(match.group(1)) == "python":
					return Python()
				elif str.lower(match.group(1)) == "jython":
					return Jython()
				else:
					raise Exception("Unknown interpreter specified")
						
			# Default to Jython, if we couldn't find anything else
			return Jython()
		else:
			# RobotFramework directory or .tsv, etc
			return RobotFramework()
	
## Get command-line arguments
parser = argparse.ArgumentParser(description='''Execute a test''',)
parser.add_argument('--logLevel',  type=str, help="Loging Level (TRACE, DEBUG, INFO, WARN, ERROR")
parser.add_argument('--screenshotLogLevel',  type=str, help="Loging Level for Screenshot captures (TRACE, DEBUG, INFO, WARN, ERROR")
parser.add_argument('--background', action='store_true', help="Run in background")
parser.add_argument('--python', action='store_true', help="Run using python interpreter")
parser.add_argument('target', help="target to execute")

parser.add_argument('--variableFile', type=str, nargs=1, help="RIDE ArgumentFile, not implemented yet")
parser.add_argument('--listener', type=str, nargs=1, help="RIDE Listener, not implemented yet")
parser.add_argument('--absolute', action='store_true', help="Use absolute path for post processing files")

parser.add_argument('arguments', metavar='arguments', type=str, nargs='*', help='optional arguments')

args = parser.parse_args()
##

if args.logLevel:
	os.environ['LOGLEVEL'] = args.logLevel

if args.screenshotLogLevel:
	os.environ['LOGLEVEL_SCREENSHOTS'] = args.screenshotLogLevel
		
	
# Setup anything that might be missing on path for Windows / Mac
print os.name
if os.name == 'posix':
	os.environ['PATH'] = os.environ['PATH'] + r':/Applications/VMware Fusion.app/Contents/Library'  

else:
	os.environ['Path'] = os.environ['Path'] + r';.\libs;C:\Program Files (x86)\Java\jre6\bin;C:\Program Files\Java\jre6\bin;'
	os.environ['PYTHONPATH'] = r'C:\Python27\DLLs;C:\Python27\lib;C:\Python27\lib\plat-win;C:\Python27\lib\lib-tk;C:\Python27;C:\Python27\lib\site-packages;C:\Program Files (x86)\Java\jre6\bin;.'

# Get launch target 
target = TargetFactory.getTarget(args.target)

if args.absolute:
	target.setUseAbsolutePostProcessingPath(True)
else:
	target.setUseAbsolutePostProcessingPath(False)

# Fixup Arguments
arguments = []
for index, arg in enumerate(args.arguments):
	arguments.append(string.replace(arg, "/", "--")) # Modify slash to mean -- to support '--' style variables (robotframework needs it)

# If an arguments file was supplied, parse it and add the arguments

if args.variableFile:
	arguments.append('--variableFile ' + args.variableFile[0])

target.setArgs(arguments)
						
# Get launch arguments
launchArgs = target.getLaunchArgs()

# Launch
print "Launching %s [%s]...\n%s" % (target.getType(), args.target, ' '.join(launchArgs))
try:
	
	p = subprocess.Popen(' '.join(launchArgs), shell=True)
	
	if not args.background:
		out, err = p.communicate()
		
		if out: print "stdout=", out
		if err: print "stderr=", err
	
	# Perform any processing if successful
	if not args.background:
		target.postProcessing()
	
	
except KeyboardInterrupt, e:

	# Fixing terminal, for some reason terminal is messed up if you press ctrl-c
	if os.name == 'posix':
		subprocess.call('reset')		

