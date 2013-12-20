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
    eventTime1_sound = 1.0 #in seconds. Instant of time when the soundGen is executed.
    eventTime2_movement = 3.0 #in seconds. Instant of time when movement ceases to be considered for reward
    eventTime3_trialEnd = 7.0 #in seconds. Instant of time when the trial ends.
    durationTotal = eventTime1_sound + eventTime2_movement + eventTime3_trialEnd
    ##
    timeWindowDivider = 10.0
    initialWindowThreshold = 1
    maxWindowThreshold = 5
    
    initialMovementThreshold = 200
    maxMovementThreshold = 1000
    movementThreshold = initialMovementThreshold #amount of movement after which movement is considered '1'
    movementVectorLength = 15 #length of vector, should be greater than movementVectorCount
    movementVectorCount = 8 #number of elements from vector to be looked at as 1 when detecting movement
    
    soundGenDuration = eventTime1_sound
    soundGenFrequency1 = 1000.0
    soundGenFrequency2 = 2000.0
    
    trialCount = 0 #total number of trials
    successTrialCount=0 #total number of succesful trials
    successRate = 0 #success rate = (success trials / total trial count) %
    dropReleased = 0 #0: no drop of water released this trial, 1: drop of water released
    trialExecuting = False #if true, the trial is online and working. Else, it has been stopped or never started
    
    countMovement = 0 #if it reaches 10, there has been detected a sustained movement for 1000 ms => give reward
    countIdleTime = 0 #if it reaches 10, there has NOT been detected a sustained movement for 1000 ms => reset counters
    
    #video Detection:
    videoDet=0 # video Detection object. initialized in the main.
    
    start_time = timeit.default_timer() #time when training with tone started.
    current_trial_start_time = timeit.default_timer() #current trial in execution, absolute time it started
    current_trial_time = timeit.default_timer() #second of the current trial (between 0 and the maximum length of a trial)
    
    current_trial_number = 0 #0: tone, 1: movement detection, 2: inter-trial, 3: instant before changing to 0

            
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
    print 't/T: increase/decrease threshold (10 - %d)' % gVariables.maxMovementThreshold
    print 'e/E: increase/decrease threshold count (1 - %d)' % gVariables.movementVectorLength
    print 'w/W: increase/decrease movement window (1 - %d sec)' % gVariables.maxWindowThreshold
    print 'k: set 8 second trial training'
    print 'l/L: recalibrate Video Input with/without noise filtering.'
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
                    gVariables.successRate = tempS
                    gVariables.display.updateInfo("% s/t", gVariables.successRate)
    gVariables.display.renderAgain()

def loopFunction():
    print gVariables.trainingName
    import sphereVideoDetection
    gVariables.videoDet = sphereVideoDetection.sphereVideoDetection(VIDEOSOURCE, CAM_WIDTH, CAM_HEIGHT)
    gVariables.movementVector = [] #has the history of previous movements, separated by 0.1 seconds
    for i in range (0, gVariables.movementVectorLength):
        gVariables.movementVector.append(0)
    print gVariables.movementVector
    #Display initialization.
    initDisplay()
    try:
        while(True):
                trialLoop()
                gVariables.videoDet.resetX()
                gVariables.videoDet.resetY()
                time.sleep(movementWindow / gVariables.timeWindowDivider)
                #####################
                updateDisplayInfo()
                #####################
                gVariables.movementVector[0:-1] = gVariables.movementVector[1:]
                gVariables.movementVector[gVariables.movementVectorLength-1] = (abs(gVariables.videoDet.getAccumX() * gVariables.videoDet.getAccumX())  + abs( gVariables.videoDet.getAccumY()*gVariables.videoDet.getAccumY() ))
                if (gVariables.movementVector[gVariables.movementVectorLength-1] >= gVariables.movementThreshold):
                    gVariables.movementVector[gVariables.movementVectorLength-1] = 1
                else:
                    gVariables.movementVector[gVariables.movementVectorLength-1] = 0
                gVariables.logger.debug('Movement Vector: %s',gVariables.movementVector)
                
                thresholdReached = True
                for i in range (gVariables.movementVectorLength-1 - gVariables.movementVectorCount, gVariables.movementVectorLength-1):
                    if (gVariables.movementVector[i] == 0):
                        thresholdReached = False
                        break
                if (thresholdReached == True):
                    #there are n 1's in a row, give Reward
                    thresholdReached = True
                    giveReward()
                    
    finally:
        return


def trialLoop():
            #This function controls all events that defines a trial: Tone at a given time, reward opportunity, etc.
            gVariables.current_trial_time = (timeit.default_timer() - gVariables.current_trial_start_time)
            #print gVariables.current_trial_time
            
            if (gVariables.trialExecuting == True):
                if (gVariables.current_trial_number == 3 ):
                    gVariables.logger.info('Starting trial:%d' % gVariables.trialCount)
                    gVariables.trialCount+=1
                    gVariables.dropReleased = 0
                    gVariables.current_trial_start_time = timeit.default_timer()
                    gVariables.logger.info('tone 1: 1 kHz')
                    gVariables.s1.play()
                    gVariables.current_trial_number = 0
                if ( int(gVariables.current_trial_time) >= gVariables.eventTime1_sound and 
                     int(gVariables.current_trial_time) <= gVariables.eventTime2_movement 
                     and gVariables.current_trial_number == 0):
                    gVariables.logger.info('Start trial movement detection')
                    gVariables.movementVector = [ 0 for i in range(gVariables.movementVectorLength)]
                    gVariables.current_trial_number = 1
                elif (int(gVariables.current_trial_time) >= gVariables.eventTime2_movement and 
                      gVariables.current_trial_number == 1):
                    gVariables.logger.info('End trial movement detection')
                    gVariables.logger.info('Start inter-trial delay')
                    gVariables.current_trial_number = 2
                elif (int(gVariables.current_trial_time) >= gVariables.eventTime3_trialEnd and
                      gVariables.current_trial_number == 2):
                    gVariables.trialTime = 0
                    gVariables.logger.info('End trial:%d' % gVariables.trialCount)
                    if(gVariables.dropReleased==1):
                        gVariables.logger.info('Trial succesful')
                    else:
                        gVariables.logger.info('Trial not succesful')
                    gVariables.logger.info('Success rate:%r' % (gVariables.successRate))
                    gVariables.current_trial_number = 3


def restartTraining():
        print "Restarting."
        try:
            import timeit
            gVariables.start_time = timeit.default_timer()
            gVariables.current_trial_start_time = timeit.default_timer()
        except:
            pass
        gVariables.current_trial_number = 3
        gVariables.trialCount = 0
        gVariables.successTrialCount=0
        gVariables.trialExecuting = True
    
def stopTraining():
        gVariables.trialExecuting = False


def giveReward():
    if (gVariables.dropReleased == 0):
        if (gVariables.current_trial_number == 1):
            #print "Release drop of water."
            gVariables.valve1.drop()
            gVariables.logger.debug("Release drop of water.")
            gVariables.successTrialCount+=1
            gVariables.dropReleased = 1

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
    
    formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    dateformat = '%Y/%m/%d %I:%M:%S %p'
    
    

    logging.basicConfig(filename='logs/training_4_%s.log' % (time.strftime("%Y-%m-%d")), filemode='a',
    level=logging.DEBUG, format=formatter, datefmt = dateformat)

    gVariables.logger = logging.getLogger('main')
    gVariables.logger.info('===============================================')
    gVariables.logger.info('Start Training 4')
    #end logging
    #valve:
    import valve
    gVariables.valve1 = valve.Valve()
    #soundGen
    import soundGen
    gVariables.s1 = soundGen.soundGen(gVariables.soundGenFrequency1, gVariables.soundGenDuration)
    gVariables.s2 = soundGen.soundGen(gVariables.soundGenFrequency2, gVariables.soundGenDuration)
    #variables to be used as calibration
    gVariables.movementThreshold = gVariables.initialMovementThreshold
    movementWindow = gVariables.initialWindowThreshold
    gVariables.trialTime = 0
    gVariables.trialExecuting = 0 #boolean, if a 8 second with tone trial is wanted, this shoulb de set to 1
    # Create thread for executing detection tasks without interrupting user input.
    fred1 = threading.Thread(target=loopFunction)
    fred1.start()
    time.sleep(1.5)
    printInstructions()
    try:
        while(True):
            try:
                key = sys.stdin.read(1)#cv2.waitKey(100) #in miliseconds
                if (key == 'o'): #escape pressed
                    gVariables.logger.info('valve open')
                    gVariables.valve1.open()
                elif (key == 'c'):
                    gVariables.logger.info('valve close')
                    gVariables.valve1.close()
                elif (key == 'd'):
                    gVariables.logger.info('valve drop')
                    gVariables.valve1.drop()
                elif (key == '1'):
                    gVariables.logger.info('tone 1: %d Hz' % gVariables.soundGenFrequency1)
                    gVariables.s1.play()
                elif (key == '2'):
                    gVariables.logger.info('tone 2: %d Hz'% gVariables.soundGenFrequency2)
                    gVariables.s2.play()
                elif (key == 't'):
                    gVariables.movementThreshold += 10
                    if gVariables.movementThreshold > gVariables.maxMovementThreshold:
                        gVariables.movementThreshold = gVariables.maxMovementThreshold
                    print "Movement Threshold changed to : " + str(gVariables.movementThreshold)
                    printInstructions()
                elif (key == 'T'):
                    gVariables.movementThreshold -= 10
                    if gVariables.movementThreshold < 10:
                        gVariables.movementThreshold = 10
                    print "Movement Threshold changed to : " + str(gVariables.movementThreshold)
                    printInstructions()
                elif (key == 'e'):
                    gVariables.movementVectorCount += 1
                    if gVariables.movementVectorCount > gVariables.movementVectorLength:
                        gVariables.movementVectorCount = gVariables.movementVectorLength
                    print "Movement Vector count changed to : " + str(gVariables.movementVectorCount)
                    printInstructions()
                elif (key == 'E'):
                    gVariables.movementVectorCount -= 1
                    if gVariables.movementVectorCount < 1:
                        gVariables.movementVectorCount = 1
                    print "Movement Vector count changed to : " + str(gVariables.movementVectorCount)
                    printInstructions()
                elif (key == 'l'):
                    gVariables.videoDet.calibrate()
                    gVariables.videoDet.setNoiseFiltering(True)
                elif (key == 'L'):
                    gVariables.videoDet.calibrate()
                    gVariables.videoDet.setNoiseFiltering(False)
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
                    if gVariables.trialExecuting == 0:
                        restartTraining()
                        print "8 second trial activated:"
                        print "  %d second: tone" %gVariables.soundGenDuration
                        print "  2 second: detection of movement"
                        print "  4 second: inter trial delay time"
                        
                    else:
                        gVariables.trialExecuting = 0
                        stopTraining()
                        print "8 second trial deactivated."
                        
                elif (key=='\x1b' or key=='q'):
                    print "Exiting."
                    gVariables.logger.info('Exit signal key = %s',key)
                    import signal
                    os.kill(os.getpid(), signal.SIGINT)
                    sys.exit()
                else :
                    print "another key pressed"
            except IOError: pass
            
            #print trialTime
            time.sleep(.05)
    except:
        print "Closing Training 4."
    finally:
        print "."
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        gVariables.logger.info('End Training 4')
        print "-"
        import os
        os._exit(0)
