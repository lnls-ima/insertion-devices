'''
Created on 22 de set. de 2021

@author: labimas
'''
import numpy as np
from imaids import models
from scipy import interpolate
import os
import matplotlib.pyplot as plt 
from datetime import date




def Shim_Signature(nested_dict, nr_periods, fname):

#nested_dict = {'cid':{0:0.25, 5:0.5},'cse':{1:0.3}} example
    delta = models.DeltaSabia(nr_periods = nr_periods)
    cassettes = delta.cassettes
    data_atual = date.today()
    
    filepath = os.path.dirname(os.path.abspath(__file__))
 
    
    for m, cassette_name in enumerate(nested_dict):
        dicts = nested_dict[cassette_name]
        for n, position in enumerate(dicts):

            shim = dicts[position]
            Blocks = cassettes[cassette_name].blocks
            Block = cassettes[cassette_name].blocks[position]
            if ((position <= 4) or (position >= 5+4*nr_periods)):
                if (position <= 4):
                    if ((Block.magnetization)[1] > 0):
                        blocktype = "Ba"
                        b_positions_sig = position
                    elif ((Block.magnetization)[1] < 0):
                        blocktype = "Bb"
                        b_positions_sig = position
                    elif ((Block.magnetization)[2] < 0):
                        blocktype = "Bc"
                        b_positions_sig = position
                    elif ((Block.magnetization)[2] > 0):
                        blocktype = "-Bc"
                        b_positions_sig = position
                        
                elif (position >= 5+4*nr_periods):   
                    if ((Block.magnetization)[1] > 0):
                        blocktype = "Ba"
                        b_positions_sig = 89
                    elif ((Block.magnetization)[1] < 0):
                        blocktype = "Bb"
                        b_positions_sig = 91
                    elif ((Block.magnetization)[2] < 0):
                        blocktype = "bc"
                        b_positions_sig = 90
                    elif ((Block.magnetization)[2] > 0):
                        blocktype = "-Bc"
                        b_positions_sig = 92
            
            elif ((position > 4) and (position < 5+4*nr_periods)):
                if ((Block.magnetization)[1] > 0):
                    blocktype = "Ba"
                    b_positions_sig = 41
                elif ((Block.magnetization)[1] < 0):
                    blocktype = "Bb"
                    b_positions_sig = 43
                elif ((Block.magnetization)[2] < 0):
                    blocktype = "Bc"
                    b_positions_sig = 42
                elif ((Block.magnetization)[2] > 0):
                    blocktype = "-Bc"
                    b_positions_sig = 40
                    
                    
            direction = np.array([b.longitudinal_position for b in Blocks])
            direction -= (direction[0] + direction[-1])/2  
            
            delta_fullperiod = models.DeltaSabia()
            cassettes_fullperiod = delta_fullperiod.cassettes
            Blocks_fullperiod = cassettes_fullperiod[cassette_name].blocks
            direction_fullperiod = np.array([b.longitudinal_position for b in Blocks_fullperiod])
            direction_fullperiod -= (direction_fullperiod[0] + direction[-1])/2      
                    
            if (n == 0):
                Signature = np.loadtxt(filepath + "\Signature_cid_Block" \
                                       + str(b_positions_sig) + "_Shim" + str(shim) + "_" + blocktype + ".txt",
                                       dtype=float, unpack=True, skiprows = 17)
                
                Signature = np.transpose(Signature)
            
                Field_errors1 = np.loadtxt(fname, dtype=float, unpack=True, skiprows = 21)
                Field_errors1 = np.transpose(Field_errors1)
                
            
                Field_errors1 = Field_errors1[(Field_errors1[:,0] == 0) & (Field_errors1[:,1] == 0),:]
                Field_errors3 = np.array([x for x in Field_errors1])
                Field_errors2 = Field_errors1[(Field_errors1[:,2] >= min(Signature[:,2])) & (Field_errors1[:,2] <= max(Signature[:,2])),:]
    
                    
                long1 = Signature[:,2]                
                long2 = Field_errors2[:,2]
            
                    
                Signature = Signature[:,3:]
                Signature1 = np.zeros(3*np.shape(Signature)[0])
                Signature1 = np.reshape(Signature1, (np.shape(Signature)[0],3))
            
                if(cassette_name == 'cse'):
                    Signature1[:,0] = (-1)*Signature[:,0]
                    Signature1[:,1] = (-1)*Signature[:,1]
                    Signature1[:,2] = Signature[:,2]
                
                elif(cassette_name == 'csd'):
                    Signature1[:,0] = Signature[:,1]
                    Signature1[:,1] = (-1)*Signature[:,0]
                    Signature1[:,2] = Signature[:,2]
            
                elif(cassette_name == 'cie'):
                    Signature1[:,0] = (-1)*Signature[:,1]
                    Signature1[:,1] = Signature[:,0]
                    Signature1[:,2] = Signature[:,2]
                
                elif(cassette_name == 'cid'):
                    Signature1 = Signature
                
  

                signature1_interpol_shift = interpolate.interp1d(long1 + direction[position] - direction_fullperiod[b_positions_sig], 
                                                                 Signature1,bounds_error = False, 
                                                                 fill_value = 0, axis = 0)
                signature1_after_interpolate = signature1_interpol_shift(long2)
            
            

                Field_errors = Field_errors2[:,3:] + signature1_after_interpolate
                
            elif (n != 0):
            
                Signature = np.loadtxt(filepath + "\Signature_cid_Block" \
                                       + str(b_positions_sig) + "_Shim" + str(shim) + "_" + blocktype + ".txt",
                                       dtype=float, unpack=True, skiprows = 17)
                        
                Signature = np.transpose(Signature)
                Signature = Signature[:,3:]
                Signature1 = np.zeros(3*np.shape(Signature)[0])
                Signature1 = np.reshape(Signature1, (np.shape(Signature)[0],3))
            
                if(cassette_name == 'cse'):
                    Signature1[:,0] = (-1)*Signature[:,0]
                    Signature1[:,1] = (-1)*Signature[:,1]
                    Signature1[:,2] = Signature[:,2]
                
                elif(cassette_name == 'csd'):
                    Signature1[:,0] = Signature[:,1]
                    Signature1[:,1] = (-1)*Signature[:,0]
                    Signature1[:,2] = Signature[:,2]
        
                elif(cassette_name == 'cie'):
                    Signature1[:,0] = (-1)*Signature[:,1]
                    Signature1[:,1] = Signature[:,0]
                    Signature1[:,2] = Signature[:,2]
                
                elif(cassette_name == 'cid'):
                    Signature1 = Signature
                 
                 

                signature1_interpol_shift = interpolate.interp1d(long1 + direction[position] - direction_fullperiod[b_positions_sig], 
                                                                 Signature1,bounds_error = False, 
                                                                 fill_value = 0, axis = 0)
                signature1_after_interpolate = signature1_interpol_shift(long2)
            
                
                Field_errors += signature1_after_interpolate
                
        if (m == 0):
            Field_errors4 = np.array([ x for x in Field_errors])    
        elif (m != 0):
            Field_errors4 += Field_errors
          
          
                
    for i in range(0,3):
        Field_errors3[(Field_errors3[:,2] >= min(long1)) & (Field_errors3[:,2] <= max(long1)),3+i] = Field_errors4[:,i]
    
                
    long3 = Field_errors3[:,2]
            
            
    filename = "Longitudinal_Magnetic_Field_Delta_Sabia.txt"
    file = open(filename,'w')
    a_file = open(fname)
    lines_to_read = np.linspace(0,20,21)

    for number, line in enumerate(a_file):

        if number in lines_to_read:
            if (number == 0):
                header = 'timestamp:\t{}\n '.format(data_atual)  
                file.writelines(header) 
            elif (number != 0):
                header = line
                file.writelines(header)   
    file.close()
    file = open(filename,'a')
    np.savetxt(file, Field_errors1)
    file.close()
    
    for i in range (0,3):
        plt.plot(long2/10, (Field_errors4[:,i])*10000)
        plt.title("Magnetic Field with Shim Signature Applied 1")
        plt.xlabel("Longitudinal direction [cm]")
        plt.ylabel("Magnetic Field [G]")
        plt.grid()
        plt.show() 
        plt.clf()
        
        
    for i in range (0,3):
        plt.plot(long3/10, (Field_errors3[:,3+i]-Field_errors1[:,3+i])*10000)
        plt.title("Magnetic Field with Shim Signature Applied 3")
        plt.xlabel("Longitudinal direction [cm]")
        plt.ylabel("Magnetic Field [G]")
        plt.grid()
        plt.show() 
        plt.clf()
        
  
    
