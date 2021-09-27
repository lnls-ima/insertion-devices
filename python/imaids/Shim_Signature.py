'''
Created on 22 de set. de 2021

@author: labimas
'''
from imaids import models
import numpy as np
from time import ctime
import matplotlib.pyplot as plt 


def Shim_Signature(Positions, Shim, fname):
    

    
    delta = models.DeltaSabia()
    
    CSE = delta.cassettes['cse']
    CSD = delta.cassettes['csd']
    CIE = delta.cassettes['cie']
    CID = delta.cassettes['cid']

    CSElist_errors = CSE.get_random_errors_magnetization_list(max_amplitude_error = 0.01, max_angular_error = np.pi/180)
    delta.create_radia_object(magnetization_dict = {'cse':CSElist_errors})
    CSDlist_errors = CSD.get_random_errors_magnetization_list(max_amplitude_error = 0.01, max_angular_error = np.pi/180)
    delta.create_radia_object(magnetization_dict = {'csd':CSDlist_errors})
    CIElist_errors = CIE.get_random_errors_magnetization_list(max_amplitude_error = 0.01, max_angular_error = np.pi/180)
    delta.create_radia_object(magnetization_dict = {'cie':CIElist_errors})
    CIDlist_errors = CID.get_random_errors_magnetization_list(max_amplitude_error = 0.01, max_angular_error = np.pi/180)
    delta.create_radia_object(magnetization_dict = {'cid':CIDlist_errors})
    
    delta.solve()
    
    x = np.zeros(16000)
    x = np.reshape(x, newshape = (16000,1)) 
    
    long = np.linspace(-800, 800, 16000)
    long = np.reshape(long, newshape=(16000,1))
    
    Field_0_errors = delta.get_field(z = long)

    time = ctime()

    header = ["timestamp:   {}\n\
    magnet_name:    DeltaSabia\n\
    gap[mm]:    13.6 \n\
    period_length[mm]:    52.5\n\
    magnet_length[mm]:    1197.63\n\
    dP[mm]:        -13.125\n\
    dCP[mm]:    0\n\
    dGV[mm]:    26.25\n\
    dGH[mm]:    0\n\
    posCSD[mm]:    26.25\n\
    posCSE[mm]:    13.125\n\
    posCID[mm]:    -13.125\n\
    posCIE[mm]:    0  \n\
    polarization:    LHCircularPolarizationZero\n\
    field_phase[deg]:    0\n\
    K_Horizontal:    0.0\n\
    K_Vertical:    0.0\n\
    K:        0.0\n\
    \n\
    X[mm]    Y[mm]    Z[mm]    Bx[T]    By[T]    Bz[T] \n\
    ------------------------------------------------------------------------------------------------------------------------------------------------------------------\n" .format(time)]
    
    
    for u in Positions:

        cassettes = delta.cassettes[u]  
    
        
        c_positions = u.upper()

        
        b_positions = Positions[u]
        height = Shim[u]
        
        for m in range(0, len(b_positions)):
            Blocks = cassettes.blocks[b_positions[m]]
            print(b_positions[m])
            if ((b_positions[m] <= 5) or (b_positions[m] >= 88)):
                if ((Blocks.magnetization)[1] > 0):
                    blocktype = "Ba"
                elif ((Blocks.magnetization)[1] < 0):
                    blocktype = "Bb"
                elif ((Blocks.magnetization)[2] < 0):
                    blocktype = "Bc"
                elif ((Blocks.magnetization)[2] > 0):
                    blocktype = "-Bc"
            
            elif ((b_positions[m] > 5) and (b_positions[m] < 88)):
                if (( u == 'cse') or (u == 'csd')):
                    if ((Blocks.magnetization)[1] > 0):
                        blocktype = "Ba"
                        b_positions[m] = 43
                    elif ((Blocks.magnetization)[1] < 0):
                        blocktype = "Bb"
                        b_positions[m] = 41
                    elif ((Blocks.magnetization)[2] < 0):
                        blocktype = "Bc"
                        b_positions[m] = 40
                    elif ((Blocks.magnetization)[2] > 0):
                        blocktype = "-Bc"
                        b_positions[m] = 42
                        
                elif (( u == 'cie') or (u == 'cid')):
                    if ((Blocks.magnetization)[1] > 0):
                        blocktype = "Ba"
                        b_positions[m] = 41
                    elif ((Blocks.magnetization)[1] < 0):
                        blocktype = "Bb"
                        b_positions[m] = 43
                    elif ((Blocks.magnetization)[2] < 0):
                        blocktype = "Bc"
                        b_positions[m] = 42
                    elif ((Blocks.magnetization)[2] > 0):
                        blocktype = "-Bc"
                        b_positions[m] = 40
            

            Signature = np.loadtxt(r"C:/Users/labimas/eclipse-workspace/Signature/Signature_" + u + "_Block" \
                                   + str(b_positions[m]) + "_Shim" + str(height[m]) + "_" + blocktype + ".txt",
                                    dtype=float, unpack=True, skiprows = 17)
            
            Field_errors1 = np.loadtxt(fname, dtype=float, unpack=True, skiprows = 17)
            Field_errors1 = np.transpose(Field_errors1)
            
            Signature = np.transpose(Signature)
            Field_errors = Field_errors1 + Signature[:,3:]

            
    Field_errors = np.hstack((long, Field_errors))
    Field_errors = np.hstack((x, Field_errors)) 
    Field_errors = np.hstack((x, Field_errors))
            
            
    filename = "Longitudinal_Magnetic Field_Delta_Sabia_.txt"
    file = open(filename,'w')
    file.writelines(header)           
    file.close()
    file = open(filename,'a')
    np.savetxt(file, Field_errors)
    file.close()
    
    for i in range (0,3):
        plt.plot(long/10, (Field_errors[:,3+i ])*10000)
        plt.title("Magnetic Field with Shim Signature Applied")
        plt.xlabel("Longitudinal direction [cm]")
        plt.ylabel("Magnetic Field [G]")
        plt.show() 
        plt.clf()
        
    for i in range (0,3):
        plt.plot(long/10, (Field_errors[:,3+i ]-Field_0_errors[:,i])*10000)
        plt.title("Magnetic Field with Shim Signature Applied")
        plt.xlabel("Longitudinal direction [cm]")
        plt.ylabel("Magnetic Field [G]")
        plt.show() 
        plt.clf()
    
Shim_Signature(Positions = {'cse':[0,2,36,40,92]}, Shim = {"cse":[0.05,0.1,0.5,0.5,0.5]})