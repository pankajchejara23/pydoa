"""
      ReAudio: Library for generating interaction network and speech feature from data captured using ReSpeaker 4 Mic version 1
      Developer: Pankaj Chejara
      Date: 8/07/2019
"""

# Import package
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from collections import Counter
import networkx as nx
import sys
import statistics
import datetime
class ReAudio(object):

    """
    Arguemnts: file_name
               Specify the name of file which contains records in format (group,timestamp,degree) and has a csv extention
    """
    def __init__(self,file_name):
        # Setting name of the log file
        self.file_name = file_name

        # Dictionary to store direction for each user
        self.Directions = {1:[],2:[],3:[],4:[]}

        # Open the audio log file with three columns group, timestamp, degree
        self.file = pd.read_csv(self.file_name,names=["group","timestamp","degree"])
        print("-------------ReAudio Library----------")
        print('Initializing.....')
        print('   Loading file')

    def getGroups(self):
        return self.file.group.unique()


    """
    This function returns pandas dataframe for a particular group.
    Argument: group
          Speficy the name of group to retrieve its dataframe.
    """
    def getGroupFrame(self,group):
        # Using pandas loc function to filter data
        temp_df = self.file.loc[self.file["group"]==group,:]

        # return the dataframe
        return temp_df


    """
    getHighestFourDegrees: This function will search through the file and extract four degrees corresponding to users.
                           It simply count the degree frequency and return four degrees with highest frequencies.

    Arguemnts: plot (Boolean)
              Setting this argument to True with plot all degrees found in the file.
    """
    def getHighestFourDegrees(self,plot,group='group-1'):
        try:
            # Read the file

            selfdf = self.file.copy()
            #print(type(selfdf))
            #print(selfdf)
            # Extract data for specified group
            temp_df = selfdf.loc[selfdf['group']==group,:]

            # Count the frequency of each degree in the file
            degree_frequency = Counter(temp_df['degree'])

            # Plot the bar graph for degree frequency if plot = True
            if plot:
                plt.bar(degree_frequency.keys(),degree_frequency.values(),width=10)
                plt.xlabel('Direction of arrival')
                plt.ylabel('Frequency')
                plt.title('Frequncy distribution of DoA (Direction of Arrival)'+group)
                plt.show()

            # Sort the degrees on the basis of their counted frequency
            sorted_deg_freq = sorted(degree_frequency.items(),key=lambda x:x[1])

            # Take six degree with higher frequencies
            highest_degrees = sorted_deg_freq[:-6]


            # Sort the order of highest degrees and return
            highest_degrees = sorted(highest_degrees,key=lambda x:x[0])

            high_four_degrees = []
            # Get four highest degrees

            for item in highest_degrees:

                # If the list is emtpy
                if len(high_four_degrees)==0:
                    high_four_degrees.append(item[0])
                else:
                    # Check whether degrees are not close to already added degree
                    if abs(item[0]-high_four_degrees[-1])%360 > 10:

                        # if not then add it to the list
                        high_four_degrees.append(item[0])
                    else:
                        # If degree is close to already added degree then add the one with higher frequency
                        if item[1]>degree_frequency[high_four_degrees[-1]]:
                            high_four_degrees.remove(high_four_degrees[-1])
                            high_four_degrees.append(item[0])
                        else:
                            pass

            # Return the four most occuring degrees
            return high_four_degrees[-4:]

        except Exception as e:
            print('Exception:',sys.exc_info())




    """
    assignUserLabel: This function assigns the user identifier (1,2,3,4) on the basis of direction of arrival of sound.
                     This function assumes that participants are sitting clockwise around ReSpeaker and first participant sitting at zero degree.

                     For orientation specification, please see this picture


    """
    def assignUserLabel(self,group='group-1'):
        # Get four highly occuring direction of arrival
        #highDegrees = self.getHighestFourDegrees(plot=False,group=group)
        highDegrees = [45,135,225,315]

        # Considering degrees in ascending order corresponds to user1 to user4
        users = np.array([item for item in highDegrees])


        # This function takes the degree and check to which highly occruing degree it is more close to.
        def assign_label(degree):

            # Computer the absolute difference between four highly occuring degree and the argument
            user_diff = np.absolute(users-degree)

            # Identifying the minimum difference
            min_diff = np.min(user_diff)


            # Getting the indices of minimum element
            indices = np.where(user_diff==min_diff)

            # Getting the first index (np.where() returns a list, therefore we need to select the first element)
            # Also np.where() returns indices (which starts from 0, whereas user identifier starts from 1.). We addedd 1 to the index to get the user identifier
            ind = indices[0]+1

            # Return the user identifier correpsonds to degree (parameter)
            #return ind[0]

            # %%%%%%%%%%%%%%%%%%%%%%%%%% Code added while analyzing annotation

            if degree > 0 and degree < 90:
                return 1
            elif degree > 90 and degree < 180:
                return 2
            if degree > 180 and degree < 270:
                return 3
            if degree > 270 and degree < 360:
                return 4



            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        # get dataframe for specified group
        temp_df = self.getGroupFrame(group)

        # Add one column to the pandas dataframe with name 'users' which contains corresponding user identifier
        temp_df.loc[:,'users'] = temp_df['degree'].map(assign_label)
        return temp_df



    """
    getSpeakingTime: This function computes the speaking time for each user

    Arguments:
        plot: Boolean argument, Specify True if you want to plot the bar graph of speaking time
        time: string, Possible values ('sec','min','hour') time unit
    """
    def getSpeakingTime(self,plot,time='sec',group='group-1'):

        # get dataframe for the specified group
        spk_df = self.assignUserLabel(group)

        # Count the frequency for each user
        speech_count = spk_df.groupby('users').count()

        # Create a dictionary for storing speaking time for each user and initialize it with zero
        user_speak_time = {1:0,2:0,3:0,4:0}


        # Iterate for each user
        for i in range(4):

            # If time unit is sec then multiply the frequency with 200/1000. As each entry represent user speaking behavior on scale of 200 ms.
            # To convert it into second, we need to multiply the frequency count for specific user with 200/1000
            if time=='sec':
                user_speak_time[i+1] = speech_count.loc[i+1,'degree']*float(200/1000)

            # Same as above but for time unit minute
            elif time=='min':
                user_speak_time[i+1] = speech_count.loc[i+1,'degree']*float(200/(60*1000))

            # For time unit hour
            elif time=='hour':
                user_speak_time[i+1] = speech_count.loc[i+1,'degree']*float(200/(60*60*1000))


        # Plot the speaking time for each user (if plot==True in the parameters)
        if plot:
            plt.figure()
            plt.bar(user_speak_time.keys(),user_speak_time.values())
            plt.ylabel('Time(%s)' % time)
            plt.xlabel('Users')
            plt.xticks(np.arange(4)+1,['user-1','user-2','user-3','user-4'])
            plt.title('Speaking time for each user')
            plt.show()
        return user_speak_time


    """
    generateEdgeFile: This function generates a file containing the edge in the form of (i,j) where i and j represents users i and user j.
                      If a user a speaks after user b then it will be considered an edge (b,a)

    """
    def generateEdgeFile(self,group):


        # dataframe for specified group
        edge_file = self.assignUserLabel(group=group)

        # Getting sequenc of speaking turn
        sequence = edge_file['users'].to_numpy()

        # Create a emplty data frame with column users and conti_frequency. Here, conti_frequency represents the continuous occurence of particular user.
        # For instance, if a user speaks then there will be many entries for that particular user because one entry recorded for every 200 ms.
        # We are considering if atleast 4 entries are found continuous then it will be treated as speaking activity.
        df = pd.DataFrame(columns=['users','conti_frequency'])


        # This function will count the number of continuous occurence
        def count_conti_occurence(index):

            # Set count to 0
            count=0

            # Starts from the given index
            j = index

            # Loop to iterate over the users sequence
            while j<len(sequence):

                # Increase the count if the element at given index (parameter) is same as the iterated element
                if sequence[j] == sequence[index]:
                    count +=1

                # If mismatch found, break the loop
                else:
                    break

                # Increases j
                j +=1

            # Return number of count for sequence[index] and index of first next occurence of different element.
            return count,(j-index)

        # Set i to 0 for the Loop
        i = 0

        # Iterate for entire sequence of users
        while i < len(sequence):

            # Call count_conti_occurence() function
            count,diff = count_conti_occurence(i)


            # Add continuous frequency of current user (sequence[i]) to the dataframe
            df = df.append({'users':sequence[i],'conti_frequency':count},ignore_index=True)


            # Move to next different element
            i = i + diff


        # We are considering speaking activtiy if there are 4 consecutive entries for one particular user
        process_df = df.where(df.conti_frequency>3)

        # Deleting other users with less than 4 consecutive entries
        process_df.dropna(axis=0,how='any',inplace=True)

        # Resultant sequence to generate edge file
        processed_sequence = process_df['users'].to_numpy()

        # Open a file to write the edges
        file  = open('edges.txt','w')

        # Create an empty list
        edge_list = list()

        # Create two variable node1 and node2 and set them to zero.
        node1=node2=0

        # Iterate over resultant users sequences
        for i in range(len(processed_sequence)):

            # For the first element
            if node1==0:
                # set node1 to the first element
                node1=processed_sequence[i]

            # For rest of the elements
            else:

                # Set the current element to node2
                node2=processed_sequence[i]

                if node1 != node2:
                    # Append the edge node1, node2 to the edge list
                    edge_list.append((node1,node2))

                    # Print the edge
                    #print("{},{}".format(node1,node2))

                    # Write the edge in the file
                    file.write("{},{}\n".format(node1,node2))

                # Set the node1 as node2
                node1=node2

        # Close the file
        file.close()


        return edge_list


    """
    drawNetwork: This function draw an interaction network from the given edge file.
                 This network is drawn as weighted graph where the thickness of edge represents the frequency of interaction between two nodes.
                 Speaking time also represented using the color.

                 Below average speaker: red
                 Above average speaker: green

    """
    def drawNetwork(self,group):

        # Generate the edge edge_list
        edge_list = self.generateEdgeFile(group)


        # Get speaking time for each user
        sp_beh = self.getSpeakingTime(plot=False,group=group)

        # Compute average speaking time
        sp_avg = sum(sp_beh.values())/float(len(sp_beh.values()))

        # Create an empty graph using networkx library
        G = nx.Graph()





            # Iterate over edge list
        for edge in edge_list:

        # Check if the current edge already exist or not
            if G.has_edge(edge[0],edge[1]):

                # Get the weight of that edge
                w = G[edge[0]][edge[1]]['weight']

                # Remove it from the graph
                G.remove_edge(edge[0],edge[1])

                # Add it again with updated weight
                G.add_edge(edge[0],edge[1],weight=w+.15)

            else:

                # If edge doesn't exist in the graph then add it with weight .5
                G.add_edge(edge[0],edge[1],weight=.5)

        # Layout for showing the network
        pos = nx.spring_layout(G)

        # Get the edges from the graph
        edges = G.edges()

        # Get the weight for every edge
        weights = [G[u][v]['weight'] for u,v in edges]

        # Generate the colormap for the each node on the basis of their speaking time
        color_map = []

        sizes=[]

        sp_total = sum(sp_beh.values())

        sp_std = statistics.stdev(sp_beh.values())





        # iterate for each node in the graph
        for node in G:

            size = float(sp_beh[node]*10)/sp_total

            sizes.append( 400 * (size+1))
            dev = float(sp_beh[node]-sp_total)/sp_std
            # Assign red color if speaking time is below average
            if dev <0:
                color_map.append('red')
            # Assign plum color if speaking time is near average
            elif dev<1 and dev>-1:
                color_map.append('plum')

            # Assign green for above average
            else:
                color_map.append('lawngreen')

        #labels = {1:'User-1',2:'Pankaj',3:'Reet',4:'Tobias'}
        # Draw the network
        nx.draw(G, pos,node_size = sizes,node_color=color_map,  edges=edges,width=weights,with_labels=True)

        # Show the network
        plt.show()
    """
    This function generate speaking time for specified time window.

    """
    def generateWindowWiseSpeakingTime(self,window_size="30S",time='sec',group='group-1'):
        # get group's dataframe
        df1=self.assignUserLabel(group)

        # Setting timestamp as datetime
        df1['timestamp'] = pd.to_datetime(df1['timestamp'])

        # Setting the index
        df1 = df1.set_index(pd.DatetimeIndex(df1['timestamp']))

        # Taking the starting time
        cur_ts = df1.timestamp[0]

        # Creating time delta from specified time window
        time_delta = pd.to_timedelta(window_size)

        # Creating a dataframe with features
        final = pd.DataFrame(columns=['timestamp','u1_speak','u2_speak','u3_speak','u4_speak','speak_sequence'])

        # loop to iterate for entire dataframe
        while cur_ts < df1.timestamp[df1.shape[0]-1]:

            # Computing the end of timewindow
            next_ts = cur_ts + time_delta

            # Getting data between two timestamps
            temp_speech_df = df1.between_time(datetime.datetime.time(cur_ts),datetime.datetime.time(next_ts),include_start=True,include_end=False)

            # Generate features out of the data
            entry = self.extractFeatures(cur_ts,temp_speech_df,time)

            # Adding the entry to the dataframe
            final = final.append(entry,ignore_index=True)

            # Moving starting timestamp to next time window
            cur_ts = next_ts

        return final

    def extractFeatures(self,timestamp,speech_df,time):
        # First user speaking time
        user1_speaking_time = 0

        # Second user speaking time
        user2_speaking_time = 0

        # Third user speaking time
        user3_speaking_time = 0

        # Fourth user speaking time
        user4_speaking_time = 0

        # String to store the speaking sequence
        speaking_sequence=""

        # Get data for each user
        us1 = speech_df.loc[speech_df['users']==1,:]
        us2 = speech_df.loc[speech_df['users']==2,:]
        us3 = speech_df.loc[speech_df['users']==3,:]
        us4 = speech_df.loc[speech_df['users']==4,:]
        multiplier = 1.0

        # Computing the timescale
        if time=='sec':
            multiplier = float(200/1000)

        # Same as above but for time unit minute
        elif time=='min':
            multiplier = float(200/(60*1000))

        # For time unit hour
        elif time=='hour':
            multiplier = float(200/(60*60*1000))

        # Computing the speaking time
        user1_speaking = us1.users.count()*multiplier
        user2_speaking = us2.users.count()*multiplier
        user3_speaking = us3.users.count()*multiplier
        user4_speaking = us4.users.count()*multiplier

        # Speaking sequence
        speaking_sequence = speech_df['users'].tolist()

        # Returning the entry
        return {'timestamp':timestamp,'u1_speak':user1_speaking,'u2_speak':user2_speaking,'u3_speak':user3_speaking,'u4_speak':user4_speaking,'speak_sequence':speaking_sequence}




    def mergeLogSpeech(self,log_file,group_ip_list={},window_size='30S'):

        df1 = pd.read_csv(log_file,names=['timestamp','ip','action','oldlen','newlen','changeset','charbank','noadd','noremove'])




        df1['addition'] = df1['newlen']-df1['oldlen']
        df1['deletion'] = df1['oldlen']-df1['newlen']
        mask = df1['addition']<0
        mask2 = df1['deletion']<0
        df1.loc[mask,'addition']=0
        df1.loc[mask2,'deletion']=0



        df1['timestamp'] = pd.to_datetime(df1['timestamp'])


        for group in self.file.group.unique():
            print ("Timestamp column found in both dataframes")

            df2 = self.assignUserLabel(group=group)
            df2['timestamp'] = pd.to_datetime(df2['timestamp'])

            df1 = df1.set_index(pd.DatetimeIndex(df1['timestamp']))
            df2 = df2.set_index(pd.DatetimeIndex(df2['timestamp']))

            if df1.timestamp[0] > df2.timestamp[0]:
                start = df1
            else:
                start = df2

            if df1.timestamp[df1.shape[0]-1] > df2.timestamp[df2.shape[0]-1]:
                last = df1
            else:
                last = df2

            ip_list=group_ip_list[group]


            cur_ts = start.timestamp[0]
            #print('Type:',type(cur_ts))
            time_delta = pd.to_timedelta(window_size)
            final = pd.DataFrame(columns=['timestamp','u1_add','u1_del','u1_text','u2_add','u2_del','u2_text','u3_add','u3_del','u3_text','u4_add','u4_del','u4_text','u1_speak','u2_speak','u3_speak','u4_speak','speak_sequence'])
            while cur_ts < last.timestamp[last.shape[0]-1]:

                next_ts = cur_ts + time_delta
                print ('Start:',cur_ts,' End:',next_ts)
                temp_log_df = df1.between_time(datetime.datetime.time(cur_ts),datetime.datetime.time(next_ts),include_start=True,include_end=False)
                temp_speech_df = df2.between_time(datetime.datetime.time(cur_ts),datetime.datetime.time(next_ts),include_start=True,include_end=False)

                entry = self.extractCombinedFeatures(cur_ts,temp_log_df,temp_speech_df,ip_list)
                #print(entry)
                #final = final.append({'timestamp':entry['timestamp'],'u1_add':entry['u1_add'],'u1_del':entry['u1_del'],'u1_text':entry['u1_text'],'u2_add':entry['u2_add'],'u2_del':entry['u2_del'],'u2_text':entry['u2_text'],'u3_add':entry['u3_add'],'u3_del':entry['u3_del'],'u3_text':entry['u3_text'],'u4_add':entry['u4_add'],'u4_del':entry['u4_del'],'u4_text':entry['u4_text'],'u1_speak':entry['u1_speak'],'u2_speak':entry['u2_speak'],'u3_speak':entry['u3_speak'],'u4_speak':entry['u4_speak'],'speak_sequence':entry['speak_sequence']},ignore_index=True)
                final = final.append(entry,ignore_index=True)

                cur_ts = next_ts

            result_file = 'audio_log_data_%s.csv'%group
            final.to_csv(result_file,index=False)





    def extractCombinedFeatures(self,timestamp,log_df,speech_df,ip_list):

        user1 = ip_list[0]
        user2 = ip_list[1]
        user3 = ip_list[2]
        user4 = ip_list[3]

        # features
        user1_addition = 0
        user1_deletion = 0
        user1_text = ""

        user2_addition = 0
        user2_deletion = 0
        user2_text = ""

        user3_addition = 0
        user3_deletion = 0
        user3_text = ""

        user4_addition = 0
        user4_deletion = 0
        user4_text = ""


        user1_speaking_time = 0
        user2_speaking_time = 0
        user3_speaking_time = 0
        user4_speaking_time = 0

        speaking_sequence=""

        u1 = log_df.loc[log_df['ip']==user1,:]
        u2 = log_df.loc[log_df['ip']==user2,:]
        u3 = log_df.loc[log_df['ip']==user3,:]
        u4 = log_df.loc[log_df['ip']==user4,:]



        us1 = speech_df.loc[speech_df['users']==1,:]
        us2 = speech_df.loc[speech_df['users']==2,:]
        us3 = speech_df.loc[speech_df['users']==3,:]
        us4 = speech_df.loc[speech_df['users']==4,:]


        def concatenate_list_data(list):

            result= ''
            for element in list:
                if str(element) != 'nan':
                    result += str(element)
            return result




        user1_addition = u1.addition.sum()
        user1_deletion = u1.deletion.sum()
        user1_text = concatenate_list_data(u1.charbank.tolist())

        user2_addition = u2.addition.sum()
        user2_deletion = u2.deletion.sum()
        user2_text = concatenate_list_data(u2.charbank.tolist())

        user3_addition = u3.addition.sum()
        user3_deletion = u3.deletion.sum()
        user3_text = concatenate_list_data(u3.charbank.tolist())

        user4_addition = u4.addition.sum()
        user4_deletion = u4.deletion.sum()
        user4_text = concatenate_list_data(u4.charbank.tolist())

        user1_speaking = us1.users.sum()*float(200/1000)
        user2_speaking = us2.users.sum()*float(200/1000)
        user3_speaking = us3.users.sum()*float(200/1000)
        user4_speaking = us4.users.sum()*float(200/1000)

        speaking_sequence = speech_df['users'].tolist()


        return {'timestamp':timestamp,'u1_add':user1_addition,'u1_del':user1_deletion,'u1_text':user1_text,'u2_add':user2_addition,'u2_del':user1_deletion,'u2_text':user2_text,'u3_add':user3_addition,'u3_del':user1_deletion,'u3_text':user3_text,'u4_add':user4_addition,'u4_del':user1_deletion,'u4_text':user4_text,'u1_speak':user1_speaking,'u2_speak':user2_speaking,'u3_speak':user3_speaking,'u4_speak':user4_speaking,'speak_sequence':speaking_sequence}
