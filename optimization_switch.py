config = { "1":["flow1","flow3","flow2"]}
def if_one_touch(config):
   one_switch = len(config)
   one_touch_ok=1
   one_touch_no_ok=0
   if one_switch is one_touch_ok:
      return one_touch_ok
   else:
      return one_touch_no_ok

myreturn=if_one_touch(config) 
print("if_one_touch : " + str(myreturn));      
