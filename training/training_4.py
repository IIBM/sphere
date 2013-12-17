# -*- coding: utf-8 -*-

######################################################
#Training 4:
"""
    
    This training creates a 1 sec tone , has an 2 second interval where the subject can
    generate movement or not, and a reward in case there has been detected continous movement. Then follows a 5 second delay
    between this and the next trial.<>
    
    Different algorithm than training_3
"""
######################################################><
import os, sys
lib_path = os.path.abspath('../modules/')
sys.path.append(lib_path)
import time
import timeit
import logging

class gVariables():
    trainingName = "Training 4"
    #relevant Training variables
    duration1_Sound = 1.0 #in seconds. Amount of time that the soundGen is executed.
    duration2_Movement = 2.0 #in seconds. Amount of time during which movement is considered
    duration3_interTrial = 4.0 #in seconds. Amount of delay time between two trials.
    ##
    timeWindowDivider = 10.0
    maxPointMovement = 2000 #above this amount of movement detected, it will be trimmed to this value.
    initialMovementThreshold = 4000
    initialWindowThreshold = 1
    maxMovementThreshold = 14000
    maxWindowThreshold = 5
    
    movementThreshold = 300
    movementVectorLength = 50 #length of vector, should be greater than movementVectorCount
    movementVectorCount = 4 #4 elements from vector to be looked at when detecting movement
    
    
    soundGenDuration = duration1_Sound
    soundGenFrequency1 = 1000.0
    soundGenFrequency2 = 2000.0
    totalTimeDuration = duration1_Sound + duration2_Movement + duration3_interTrial #in seconds
    timeThreshold_01 = 20
    timeThreshold_02 = 64
    timeThreshold_03 = 150
    
    trialCount = 0
    successTrialCount=0
    dropReleased = 0
    trialExecuting = False #if true, the trial is online and working. Else, it has been stopped or never started
    
    countMovement = 0 #if it reaches 10, there has been detected a sustained movement for 1000 ms => give reward
    countIdleTime = 0 #if it reaches 10, there has NOT been detected a sustained movement for 1000 ms => reset counters
    
    #video Detection:
    videoDet=0 #initialized on the main.
    
    import timeit
    start_time = timeit.default_timer()
    

            
    def recalculateTimeIntervals(self):
        print "recalculating time intervals."
        #Should recalculate timeThreshold_0x according to total Time DUration.
        #This should be executed by the program only once, at the beginning of the run.
    
def printInstructions():
    print 'Options:'
    print 'o: Open Valve'
    print 'c: Close Valve'
    print 'd: Water Drop'
    print '1: %d Hz tone' % gVariables.soundGenFrequency1
    print '2: %d Hz tone' % gVariables.soundGenFrequency2
    print 't/T: increase/decrease threshold (500 - %d)' % gVariables.maxMovementThreshold
    print 'w/W: increase/decrease movement window (1 - %d sec)' % gVariables.maxWindowThreshold
    print 'k: set 8 second trial training'
    print 'q or ESC: quit'

def initDisplay():
    import trainingDisplay #display for showing different variables of interest
    gVariables.display = trainingDisplay.trainingDisplay()
    gVariables.display.addImportantInfo(("Trials", 0))
    gVariables.display.addImportantInfo(("Succesful Trials", 0))
    gVariables.display.addSecondaryInfo(("% s/t",0.0))
    gVariables.display.addSecondaryInfo(("Time", 0))
    gVariables.display.renderAgain()

def updateDisplayInfo():
    if (gVariables.trialExecuting == True):
                    now = timeit.default_timer()
                    gVariables.display.updateInfo("Time", int(now - gVariables.start_time ) )
    gVariables.display.updateInfo("Trials", gVariables.trialCount)
    gVariables.display.updateInfo("Succesful Trials", gVariables.successTrialCount)
    if (gVariables.trialCount > 0):
                    temp =  (1.0*gVariables.successTrialCount/ gVariables.trialCount)
                    tempH = temp*100.0
                    tempString = str(tempH)
                    if (len(tempString) > 3):
                        tempS = str(tempH)[:4]
                    else:
                        tempS = str(tempH)[:3]
                    gVariables.display.updateInfo("% s/t", tempS)
    gVariables.display.renderAgain()

def loopFunction():
    print gVariables.trainingName
    import sphereVideoDetection
    gVariables.videoDet = sphereVideoDetection.sphereVideoDetection(VIDEOSOURCE, CAM_WIDTH, CAM_HEIGHT)
    
    movementVector = [] #has the history of previous movements, separated by 0.1 seconds
    for i in range (0, gVariables.movementVectorLength):
        movementVector.append(0)
    print movementVector
    #Display initialization.
    initDisplay()
    
    try:
        while(True):
                gVariables.videoDet.resetX()
                gVariables.videoDet.resetY()
                time.sleep(movementWindow / gVariables.timeWindowDivider)
                #####################
                #update display info
                #####################
                updateDisplayInfo()
                #####################
                movementVector[0] = movementVector[1]
                movementVector[1] = movementVector[2]
                movementVector[2] = movementVector[3]
                movementVector[3] = movementVector[4]
                movementVector[4] = movementVector[5]
                movementVector[5] = movementVector[6]
                movementVector[6] = movementVector[7]
                movementVector[7] = movementVector[8]
                movementVector[8] = movementVector[9]
                movementVector[9] = (abs(gVariables.videoDet.getAccumX() * gVariables.videoDet.getAccumX())  + abs( gVariables.videoDet.getAccumY()*gVariables.videoDet.getAccumY() ))
                if (movementVector[9]>= gVariables.maxPointMovement):
                    movementVector[9] = gVariables.maxPointMovement - 1 
                vectorSum = 0
                for i in range(0,len(movementVector)):
                    vectorSum+= movementVector[i]
                if (vectorSum  > movementThreshold):
                    gVariables.countMovement += 1
                else:
                    gVariables.countIdleTime += 1
                logger.debug('Movement Vector: %s',movementVector)
                #print "vector sum: " + str(vectorSum) + "       movement count: "+ str(countMovement)        
                logger.debug('%s',"vector sum: " + str(vectorSum) + "       movement count: "+ str(gVariables.countMovement))
                if (gVariables.countIdleTime >9):
                    #durante 1000 ms no se estuvo moviendo. Resetear contadores
                    gVariables.countMovement = 0
                    gVariables.countIdleTime = 0
                if (gVariables.countMovement > 9):
                    #se estuvo moviendo durante 1000 ms. Dar recompensa.
                    gVariables.countMovement = 0
                    for i in range(0,len(movementVector)):
                        movementVector[i] = 0
                    #print "Release drop of water."
                    if (trialTime > gVariables.timeThreshold_01 and trialTime < gVariables.timeThreshold_02 and gVariables.dropReleased == 0):
                        gVariables.valve1.drop()
                        logger.debug("Release drop of water.")
                        gVariables.successTrialCount+=1
                        gVariables.dropReleased = 1
    finally:
        return

def restartTraining():
        print "Restarting."
        try:
            import timeit
            gVariables.start_time = timeit.default_timer()
        except:
            pass
        
        gVariables.trialCount = 0
        gVariables.successTrialCount=0
        gVariables.trialExecuting = True
    
def stopTraining():
        gVariables.trialExecuting = False

if __name__ == '__main__':
    import time
    import threading
    try:
        from configvideo import *
    except ImportError:
        print "File configvideo.py not found."
    except:
        print "Error importing configvideo" 
    #logging
    import logging

    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    
    try:
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)
    
        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
    except:
        print "Error capturing input."

    time.sleep(2)

    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    dateformat = '%Y/%m/%d %I:%M:%S %p'

    logging.basicConfig(filename='logs/training4.log', filemode='a',
    level=logging.DEBUG, format=formatter, datefmt = dateformat)

    logger = logging.getLogger('main')
    logger.info('===============================================')
    logger.info('Start Training 4')
    #end logging
    #valve:
    import valve
    gVariables.valve1 = valve.Valve()
    #soundGen
    import soundGen
    s1 = soundGen.soundGen(gVariables.soundGenFrequency1, gVariables.soundGenDuration)
    s2 = soundGen.soundGen(gVariables.soundGenFrequency2, gVariables.soundGenDuration)
    #variables to be used as calibration
    movementThreshold = gVariables.initialMovementThreshold
    movementWindow = gVariables.initialWindowThreshold
    trialTime = 0
    isTrial = 0 #boolean, if a 8 second with tone trial is wanted, this shoulb de set to 1
    # Create thread for executing detection tasks without interrupting user input.
    fred1 = threading.Thread(target=loopFunction)
    fred1.start()
    time.sleep(4)
    printInstructions()
    try:
        while(True):
            try:
                key = sys.stdin.read(1)#cv2.waitKey(100) #in miliseconds
                if (key == 'o'): #escape pressed
                    logger.info('valve open')
                    gVariables.valve1.open()
                elif (key == 'c'):
                    logger.info('valve close')
                    gVariables.valve1.close()
                elif (key == 'd'):
                    logger.info('valve drop')
                    gVariables.valve1.drop()
                elif (key == '1'):
                    logger.info('tone 1: %d Hz' % gVariables.soundGenFrequency1)
                    s1.play()
                elif (key == '2'):
                    logger.info('tone 2: %d Hz'% gVariables.soundGenFrequency2)
                    s2.play()
                elif (key == 't'):
                    movementThreshold += 500
                    if movementThreshold > gVariables.maxMovementThreshold:
                        movementThreshold = gVariables.maxMovementThreshold
                    print "Movement Threshold changed to : " + str(movementThreshold)
                    printInstructions()
                elif (key == 'T'):
                    movementThreshold -= 500
                    if movementThreshold < 500:
                        movementThreshold = 500
                    print "Movement Threshold changed to : " + str(movementThreshold)
                    printInstructions()
                elif (key == 'w'):
                    movementWindow +=1
                    if movementWindow > gVariables.maxWindowThreshold:
                        movementWindow = gVariables.maxWindowThreshold
                    print "Movement Window changed to : " + str(movementWindow) + "seconds"
                    printInstructions()
                elif (key == 'W'):
                    movementWindow -=1
                    if movementWindow < 1:
                        movementWindow = 1
                    print "Movement Window changed to : " + str(movementWindow) + "seconds"
                    printInstructions()
                elif (key == 'k'):
                    if isTrial == 0:
                        isTrial = 1
                        trialTime = 0
                        restartTraining()
                        print "8 second trial activated:"
                        print "  %d second: tone" %gVariables.soundGenDuration
                        print "  2 second: detection of movement"
                        print "  4 second: inter trial delay time"
                        
                    else:
                        isTrial = 0
                        stopTraining()
                        print "8 second trial deactivated."
                        
                elif (key=='\x1b' or key=='q'):
                    print "Exiting."
                    logger.info('Exit signal key = %s',key)
                    import signal
                    os.kill(os.getpid(), signal.SIGINT)
                    sys.exit()
                else :
                    print "another key pressed"
            except IOError: pass
            if (isTrial == 1):
                trialTime +=1
                if (trialTime == 1 ):
                    logger.info('Starting new trial')
                    gVariables.trialCount+=1
                    gVariables.dropReleased = 0
                    logger.info('tone 1: 1 kHz')
                    s1.play()
                if (trialTime == gVariables.timeThreshold_01):
                    logger.info('Start trial movement detection')
                elif (trialTime == gVariables.timeThreshold_02):
                    logger.info('End trial movement detection')
                    logger.info('Start inter-trial delay')
                elif trialTime> gVariables.timeThreshold_03:
                    trialTime = 0
                    logger.info('End inter-trial delay')
            #print trialTime
            time.sleep(.05)
    except:
        print "Closing Training 3."
    finally:
        print "."
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        logger.info('End Training 3')
        print "-"
        import os
        os._exit(0)
