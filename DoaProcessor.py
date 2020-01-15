
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
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

class DoaProcessor(object):
    """
    This class provides functions to process DoA (Direction of Arrival) datafile.
    DoA data file cotains direction of sound detected by the microphone array.

    """

    def __init__(self,datafile,n):
        """


        :param datafile: Name of the DoA data file.
        :type datafile: str.
        :param n: Number of speaker.
        :param n: int.

        """

        # Setting name of the log file
        self.file_name = datafile

        # Number of Speaker
        self.n = n

        # Dictionary to store direction for each user
        if n==2:
            self.Directions = {1:[],2:[]}
        elif n==3:
            self.Directions = {1:[],2:[],3:[]}
        elif n==4:
            self.Directions = {1:[],2:[],3:[],4:[]}
        else:
            print('PyDoA support groups with size 2,3,4. Please specify a valid group size.')

        # Open the audio log file with three columns group, timestamp, degree
        self.file = pd.read_csv(self.file_name,names=["group","timestamp","degree"])
        print("PyDoA Library")
        print('[',datetime.datetime.now(),']','Initialized')
        print('[',datetime.datetime.now(),']','File loaded successfully')


    def getGroups(self):
        """
        This function extracts group information (e.g. number of groups, labels of groups)

        :returns: list -- List of group labels

        """
        return self.file.group.unique()



    def getGroupFrame(self,group):
        """
        This function extracts DoA data for a specific group.

        :param group: Group label.
        :type group: str
        :returns: Pandas DataFrame -- Dataframe with columns timestamp, directions

        """

        # Using pandas loc function to filter data
        temp_df = self.file.loc[self.file["group"]==group,:]

        # return the dataframe
        return temp_df



    def plotDegreeDistribution(self,group='group-1'):
        """
        This function plot the frequency distribution of degrees for specified group.
        It simply count the degree frequency and plot a bar graph.

        :param group: Label of group.
        :type group: str
        """
        selfdf = self.file.copy()

        # Extract data for specified group
        temp_df = selfdf.loc[selfdf['group']==group,:]

        # Count the frequency of each degree in the file
        degree_frequency = Counter(temp_df['degree'])

        # Plot the bar graph for degree frequency if plot = True

        plt.bar(degree_frequency.keys(),degree_frequency.values(),width=10)
        plt.xlabel('Direction of Arrival')
        plt.ylabel('Frequency')
        plt.title('Frequncy distribution of DoA (Direction of Arrival) for '+group)
        plt.show()


    def setDegreeForSpeaker(self,degrees):
        """
        This function set the degree for each speaker. For instance, if speakers are sitting at a particular degree (e.g. speaker-1 at 45 degree, speaker-2 at 135, etc). Those degrees can be used to differentiate among speakers.

        :param degrees: List of degree having n items.
        :type degrees: List
        """
        if self.n == len(degrees):
            for index in range(self.n):
                self.Directions[index+1] = degrees[index]
        else:
            print('Mismatch between number of speakers and number of specified degreees')


    def getPeakDegree(self,group='group-1',bins=36,sigma=2.0):
        """
        This function will find the peaks from degree distribution.
        It uses gaussian kernel to smoothify the degree distribution and then apply peak finding algorithm to detect peaks.

        :param group: Group label.
        :type group: str
        :param bins: Bin size
        :type bins: int
        :param sigma: Sigma for Gaussian kernel
        :type sigma: double
        :returns: List -- list of peak degrees

        """
        grp = self.getGroupFrame(group)
        series = grp['degree']

        count, division = np.histogram(series, bins=bins)
        count = gaussian_filter1d(count,sigma)
        peaks, props = find_peaks(count)
        plt.figure()
        plt.plot(division[:-1], count)
        plt.xlabel('Direction of Arrival')
        plt.ylabel('Frequency')
        plt.show()
        return division[peaks]



    def getHighestNdegrees(self,sep=60,group='group-1'):
        """
        This function will search through the directions for specfied group and extract  n directions with highest frequencies.
        It simply count the degree frequency and return n degrees which are seperated by  particular degrees.

        :param sep: Distance between speakers in degrees. Default values are 360/n.
        :type sep: int
        :param group: Group label.
        :type group: str
        :returns: List -- list containing n degrees with highest frequencies
        """



        try:
            # Read the file

            sep = 360/self.n - 30

            selfdf = self.file.copy()

            # Extract data for specified group
            temp_df = selfdf.loc[selfdf['group']==group,:]

            # Count the frequency of each degree in the file
            degree_frequency = Counter(temp_df['degree'])

            #print(degree_frequency)
            # Sort the degrees on the basis of their counted frequency
            sorted_deg_freq = sorted(degree_frequency.items(),key=lambda x:x[1])

            # Take six degree with higher frequencies
            highest_degrees = sorted_deg_freq[-8:]

            #print('Highest 10 degrees',highest_degrees)
            # Sort the order of highest degrees and return
            highest_degrees = sorted(highest_degrees,key=lambda x:x[0])

            #print('Highest 10 degrees',highest_degrees)
            high_four_degrees = []
            # Get four highest degrees

            for item in highest_degrees:

                # If the list is emtpy
                if len(high_four_degrees)==0:
                    high_four_degrees.append(item[0])
                else:
                    # Check whether degrees are not close to already added degree
                    if abs(item[0]-high_four_degrees[-1])%360 > sep:

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





    def assignUserLabel(self,group='group-1'):
        """
        This function assigns the user identifiers on the basis of direction of arrival of sound.
        This function assumes that participants are sitting clockwise around ReSpeaker. First participant in clockwise fasion is considered user-1 and so on.

        :param group: Group label.
        :type group: str
        :returns: DataFrame -- Pandas Dataframe with column users for each detected direction
        """
        # Get four highly occuring direction of arrival
        #highDegrees = self.getHighestFourDegrees(plot=False,group=group)
        #highDegrees = [45,135,225,315]

        highDegrees = self.Directions.values()
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
            return ind[0]


        # get dataframe for specified group
        temp_df = self.getGroupFrame(group)

        # Add one column to the pandas dataframe with name 'users' which contains corresponding user identifier
        temp_df.loc[:,'users'] = temp_df['degree'].map(assign_label)
        return temp_df




    def getSpeakingTime(self,plot,time='sec',granularity=200,group='group-1'):

        """
        This function computes the speaking time for each user.

        :param plot: Flag for plotting speaking time.
        :type plot: Bool
        :param time: Time resolusion for computing speaking time.
        :type time: str
            Possible values 'sec','min','hour'
        :param granularity: Duration of  each detected direction
        :type granularity: int
        :param group: Group Label.
        :type group: str
        :returns: List -- list containing total speaking time for each user.
        """
        # get dataframe for the specified group
        spk_df = self.assignUserLabel(group)

        # Count the frequency for each user
        speech_count = spk_df.groupby('users').count()

        # Create a dictionary for storing speaking time for each user and initialize it with zero
        user_speak_time = dict()
        for i in range(self.n):
            user_speak_time[i+1]=0


        # Iterate for each user
        for i in range(self.n):

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


        if plot:
            plt.figure()
            plt.bar(user_speak_time.keys(),user_speak_time.values())
            plt.ylabel('Time(%s)' % time)
            plt.xlabel('Users')
            xlabels = []
            for i in range(self.n):
                xlabels.append('user-%d'%(i+1))

            plt.xticks(np.arange(self.n)+1,xlabels)
            plt.title('Speaking time for each user')
            plt.show()
        return user_speak_time



    def generateEdgeFile(self,group='group-1',threshold=3,edge_filename='edge.txt'):
        """
        This function generates a file containing the edge in the form of (i,j) where i and j represents users-i and user-j, and this sequence represent their speaking order.
        If a user a speaks after user b then it will be considered an edge (b,a)

        :param group: Group Label
        :type group: str
        :param threshold: This parameter specify the threshold to consider a valid speaking activity. For instance, if direction is detected for every 200 ms then a threshold=1 implies that if a user has five consecutive entries then it will be considered as speaking activity.
        :type threshold: int
        :param edge_filename: Name of the newly generated edge file.
        :type edge_filename: str
        :returns: List -- list containing item in the form (i,j) which represent edge between user-i and user-j.
        """

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
        process_df = df.where(df.conti_frequency>threshold)

        # Deleting other users with less than 4 consecutive entries
        process_df.dropna(axis=0,how='any',inplace=True)

        # Resultant sequence to generate edge file
        processed_sequence = process_df['users'].to_numpy()

        # Open a file to write the edges
        file  = open(edge_filename,'w')

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



    def drawNetwork(self,group='group-1'):

        """
        This function draws an interaction network from the  edge file generated from speaker's speaking order.
        This network is drawn as weighted graph where the thickness of edge represents the frequency of interaction.

        :param group: Group label.
        :type group: str
        """

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
            if sp_beh[node] <= sp_avg:
                color_map.append('red')
            # Assign green for above average
            else:
                color_map.append('lawngreen')

        #labels = {1:'User-1',2:'Pankaj',3:'Reet',4:'Tobias'}
        # Draw the network
        nx.draw(G, pos,node_size = sizes,node_color=color_map,  edges=edges,width=weights,with_labels=True)

        # Show the network
        plt.show()




    def generateWindowWiseSpeakingTime(self,window_size="30S",time='sec',group='group-1'):
        """
        This function generates speaking time metric for total duration by dividing in specified time window and then computing speaking time for each of those window.

        :param window_size: Size of time window.
        :type window_size: str
            Possible values
        :param time: Time resolution of computer speaking time.
        :type time: str
            Possible values sec, min, hour

        :param group: Group label.
        :type group: str

        :returns: DataFrame -- Dataframe with columns start_time, end_time, and speaking time for each user in that window.
        """
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
