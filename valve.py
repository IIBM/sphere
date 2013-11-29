import parallel

ValvePinMask = 0x04

class dummypp () :
    def __init__(self) :
        self.data = 0

    def getData(self):
        return self.data

    def setData(self,data) :
        self.data = data
        return self.data
  
  
class valve() :
    def __init__(self) :
        try :
          self.p = parallel.Parallel()
        except :
          print "Warning!!!: Could not find any parallel port. Using dummy parallel port"
          self.p = dummypp()

    def on(self) :
        a = self.p.getData()
        return self.p.setData(a|ValvePinMask)

    def off(self) :
        a = self.p.getData()
        return self.p.setData(a&(~ValvePinMask))
    

if __name__ == '__main__':
    import time

    v1 = valve()
    print "open valve"
    v1.on()
    print "delay 2 seconds"
    time.sleep(2)
    print "close valve"
    v1.off()
