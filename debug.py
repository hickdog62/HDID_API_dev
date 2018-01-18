
##
## Debug.py: debug object class
##     Python translation of Mark Hickey's Perl debug package
##
##     Todo:
##          01/15: maybe make the env_var a base for <env_var>_LEVELS and <env_var>_DEF_FN
##                 and/or maybe <env_var>_LOGFILE
##          01/16: maybe allow an autoindent setting so the messages for each level would be 
##                 automatically indented.
##          
##
import os
import re
import json
import sys
import time
from time import strftime

class debug:
  
   
    #
    # the ubiquitous init function
    #   prog_ref is the name of the calling program
    #   env_var is an environment variable that has debug level settings
    #   def_fn is a the path of a file that contains debug level settings
    #   logfile is an output file for log messages
    #   logging indicates if logging is on or off
    #
    def __init__(self, prog_ref="",env_var="",def_fn="",logfile="",do_logging=0,do_print=1,eval="le"):
        self.prog_name = prog_ref
        self.env_var = env_var
        self.def_fn = def_fn
        self.printing = do_print
        self.logging = do_logging
        self.log_fn = logfile
        self.eval = eval
        self.indent_space=0
        self.date_fmt = "MDY"
        self.set_debug(def_fn, env_var, logfile)
        self.active = 0
    
    
    def set_debug(self,def_fn,env_var,logfile):
         #
         # if we can find the variable env_name in the
         # environment, then use it's value as the debug 
         # value.  Otherwise look for a setting for the
         # specified prog_ref in the def_fn file.  If the 
         # env var or the file are not present, do no 
         # debugging.  If the file is present, but there
         # is no entry for the prog_ref, set the variable to 
         # debug everything.
         #
         if env_var in os.environ:
             self.active = 1
             self.levels = os.environ[env_var]
       
         elif def_fn != "":
             try:
               def_file=open(def_fn, 'r')
             except IOError as e:
                print ("Failed to open debug definition file " + def_fn)
                print (e.errno)
                print(e)
                sys.exit()
            
         def_file.close
         
         self.active = 1
         json_nodes = json.load(def_file)
         for spec in json_nodes['debug_spec']:
             if spec['prog_name'] == self.prog_name:
                 self.levels = spec['levels']
                 self.printing = int(spec['printing'])
                 self.logging = int(spec['logging'])
                 self.log_fn = spec['log_file']
                 self.eval = spec['eval']
                 self.indent_space = int(spec['indent_space'])
                 self.date_fmt = spec["date_fmt"]
         
         self.levels = self.levels.replace('"','')
         self.levels = re.sub('[,| ]',':',self.levels)
         self.levels = re.sub('^',':',self.levels)
         self.levels = re.sub('$',':',self.levels)  
       
         # 
         # try to open the logging file, if specified and printing is 
         # specified
         #    
         if self.log_fn != "" and self.logging != 0:
             try:
                self.logfile=open(self.log_fn, 'w')
             except IOError as e:
                print ("Failed to open debug logging file " + self.log_fn)
                print (e.errno)
                print(e)
                sys.exit()   
         else:
            # 
            # either the log filemname was blank, or logging was off
            # set loggin to off to make sure we don't do something odd
            # later
            #
            self.logging = 0
            
            
    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    
    def display(self):
        print ("prog_name: " + self.prog_name)
        print ("log_fn: " + self.log_fn)
        print ("Levels: " + self.levels)
        print ("logging: " + str(self.logging))
        print ("printing: " + str(self.printing))
        print ("def_fn: " + self.def_fn)
        print ("env_var: " + self.env_var)
        print ("eval: " + self.eval)
        print ("indent_space: " + str(self.indent_space))
        print ("date_fmt" + self.date_fmt)

    #
    # Evaluates a major/minor debug level pair to see if debug 
    # is active for that level
    #
    def debug_level_ok(self,maj,min):
       retval = 0
       if self.active and self.levels == "all":
            return 1
        
       my_maj = str(maj)
       my_min = str(min)
       use_math = 0
       if my_min.isdigit():
           use_math = 1
        
       m = re.match('.*:' + my_maj + '\.([^:]*):.*',self.levels)  
       if m != None:
            lev_min = str(m.group(1))
            if use_math == 1:
                if not lev_min.isdigit():
                    retval = 0
                    return retval
                else:
                    if self.eval == 'le':
                        if int(my_min) <= int(lev_min) :
                            retval = 1
                    
                    if self.eval == 'ge':
                        if int(my_min) >= int(lev_min) :
                            retval = 1
            else:
                if my_min == lev_min:
                    retval = 1
       else:
           retval = 0
       
       return retval
    
    

    def debug(self, maj, min, msg):
        if self.debug_level_ok(maj, min):
            ltime = time.localtime()
            if self.date_fmt == "MDY":
                time_str = strftime("%m/%d/%Y %H:%M")
                
            if self.date_fmt == "YMD":
                time_str = strftime("%Y-%m-%d %H:%M")                
           # time_str = time.asctime()
            n_pad = min*self.indent_space
            print ("n_pad =" + str(n_pad))
            if self.printing:
                print(time_str +": " + self.prog_name + "[" + str(os.getpid()) + "] (" + str(maj) + "," + str(min) + ")" + msg.rjust(n_pad+len(msg)))
            
            if self.logging:
                self.logfile.seek(0,2)
                self.logfile.write(time_str +": " + self.prog_name + "[" + str(os.getpid()) + "] (" + str(maj) + "," + str(min) + ")" + msg.rjust(n_pad+len(msg)))
 #               #msg.rjust(n_pad+len(msg))
                
      
    
    

         
     
    

    
   
