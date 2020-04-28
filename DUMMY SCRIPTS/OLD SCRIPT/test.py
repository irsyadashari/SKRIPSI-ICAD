import time


maxWater = 50
waterTankVolume = 50
waterVolumetoChange = 5 # mengganti 1/8 volume air di dalam tank
volumeAfterDrain =  float(maxWater) - float(waterVolumetoChange)
isTankDrained = False
isWaterChangeCompleted = False

def start_water_changing():
    while isWaterChangeCompleted == False:
        if(isTankDrained == False):
            drain_half_tank()
        else :
            fill_full_tank()
            if(isWaterChangeCompleted == True):
                print("Penggantian air telah selesai")
                break
        
def drain_half_tank():
#    half = maxWater/2 #kode asli
   
    if ( waterTankVolume > float(volumeAfterDrain)):
        time.sleep(2)
        print("penyedotan sedang berlangsung...")    
        #Nyalakan pompa pengisap
        globals()['waterTankVolume'] -= 0.5
        print("\nKetinggian Air : ")
        print(waterTankVolume)
        print("Target volume air :")
        print(volumeAfterDrain)
        print("\n\n")
    else :
        #Matikan pompa pengisap
        global isTankDrained 
        isTankDrained = True
        print("penyedotan telah selesai!\n\n")
        time.sleep(1)
        
def fill_full_tank():
   
    if (float(waterTankVolume) < float(maxWater)):
        time.sleep(2)
        print("pengisian sedang berlangsung...")
         #Nyalakan pompa pengisi
        globals()['waterTankVolume'] += 0.5
        print("\nKetinggian Air : ")
        print(waterTankVolume)
        print("Target volume air :")
        print(maxWater)
        print("\n\n")
    else :
        #Matikan pompa pengisi
        print("mematikan pompa pengisi...")
        global isWaterChangeCompleted 
        isWaterChangeCompleted = True
        
start_water_changing()