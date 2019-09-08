import os
from copy import deepcopy
import random
import multiprocessing
import numpy as np
from PIL import Image,ImageDraw
from IPython.display import display


POP_PER_GEN= 50 #number of canvases generated per round, i.e. generation
MUTATION_CHANCE=0.4 #self explanatory`
ADD_GENE_CHANCE = 0.6 #again, pretty obvious... we should try tweaking with this value, maybe make it more to have a lot of genes, thus possibly increasing reso of image
REM_GENE_CHANCE = 0.4 #and... maybe have this even lower
INITIAL_GENES = 50 #obvious
GENERATIONS_PER_IMAGE = 200 #how often we're printing images

"""
This is the code for setting up global target, which is our reference image, in this case, a 640x480 pixels image of pikachu
"""

try:
    globalTarget = Image.open("pikaref.jpeg")
except IOError as e:
    print ("File pikaref.jpeg must be located in the same directory as pyointillism.py.")
    exit()

"""
Making the color and point class here... man it took an insane amount of time to understand this
"""

class Point:
  def __init__(self,x,y):
    self.x=x #okay so, here we have self.x become x... i.e. when we call a .x, it will be pointing at that variable's instantiated value of x (or so I hope)
    self.y=y#same concept here for y

"""
to make this a bit better, we can have lmao, a and b for self, x and y, but self (or lmao) should stay x, if we will eventually use a .x in the code
basically, this also works, and does the exact same thing, since we will be working with only .x's and .y's later on
def __init__(lmao,a,b):
lmao.x=a
lmao.y=b
"""

#We do not need add, since it has never been called in the main program

class Color:
  def __init__(self,r,g,b):
    self.r=r
    self.g=g
    self.b=b

#again, we never need to shift the initial vals, since they're randomized anyways, and python will always point to them once set in the selfvar instance of the class


class Gene:
    def __init__(self,size):
        self.size = size #Points to the *INSTANCE* value of size which is equal to or points to the same value as size
        self.diameter = random.randint(5,15) #Randomly sets the diameter between 5,15 <educated guess>
        self.pos = Point(random.randint(0,size[0]),random.randint(0,size[1]))
        """ 
        Now the pos instance variable points to the object 
        of Random class which is being passed with these parameters.
        """
        self.color = Color(random.randint(0,255),random.randint(0,255),random.randint(0,255)) #same as above but for Color class
        self.params = ["diameter","pos","color"] 
        """
        params holds "diameter" as a string because 
        when we mutate we, need to choose which attribute to mutate 
        not which value, hence this is just a list to hold what params we have
        """

    def mutate(self):
        """
        np.random.normal uses gaussian distribution, it is the closest to true random and much easier to use against a
        normal random.randint function. Basically it is easier to plot.
        Explanation for Params: np.random.normal(mean,std_dev, size). Size in our case is a one dimensional array 
        which stores the random values that the np.random.normal() function will return. We can call it "number of circles" in our case. 
        Other values of size can be np.random.normal(mean,std, size(3,3)). This will return random values and store them in a 3,3 matrix.
        """
        mutation_size = max(1,int(round(random.gauss(15,4))))/100
        """
        Changed the mutation by using random.randint rather than the gaussian one 
        after observing that the gaussian random never really gave an output of more than 0.25
        """

        #Decide what will be mutated, just randomly picking onr of the three params
        mutation_type = random.choice(self.params)

        #Mutate the thing
        if mutation_type == "diameter":
            """
            Over here, what we are providing a range between self.diameter*x where x=1-mutation size and self.diameter*y where =1+mutation size
            Basically we add or subtract from 1 because the mutation has to be small
            """
            self.diameter = max(1,random.randint(int(self.diameter*(1-mutation_size)),int(self.diameter*(1+mutation_size))))
            return self.diameter
            #same thing here
        elif mutation_type == "pos":
            x = max(0,random.randint(int(self.pos.x*(1-mutation_size)),int(self.pos.x*(1+mutation_size))))
            y = max(0,random.randint(int(self.pos.y*(1-mutation_size)),int(self.pos.y*(1+mutation_size))))
            self.pos = Point(min(x,self.size[0]),min(y,self.size[1]))
            return self.pos
        elif mutation_type == "color":
            r = min(max(0,random.randint(int(self.color.r*(1-mutation_size)),int(self.color.r*(1+mutation_size)))),255)
            g = min(max(0,random.randint(int(self.color.g*(1-mutation_size)),int(self.color.g*(1+mutation_size)))),255)
            b = min(max(0,random.randint(int(self.color.b*(1-mutation_size)),int(self.color.b*(1+mutation_size)))),255)
            self.color = Color(r,g,b)
            return self.color
def mutateAndTest(org):
    """
    Given an organism, perform a random mutation on it, and then use the fitness function to
    determine how accurate of a result the mutated offspring draws.
    """
    try:
        c = deepcopy(org) #for editing every value of multidimensional array(our image), without affecting original
        c.mutate()
        i1 = c.drawImage()
        i2 = globalTarget
        return (fitness(i1,i2),c)
    except KeyboardInterrupt:
        pass

def groupMutate(o,number,p):
    """
    Mutates and tests a number of organisms using the multiprocessing module.
    """
    results = p.map(mutateAndTest,[o]*number)
    return results

"""
This is the run function.
God save me.
"""

def run(cores):
    """
    First we will make a directory called images to save the files in.
    """
    if not os.path.exists("Solutions"):
        os.mkdir("Solutions")

    #f = open(os.path.join("Solutions","log.txt"),'a') #a is for append, it also creates files if not available, the rest is self explanatory

    tg = globalTarget

    generation = 1 #counter for generation, for printing every 100 gens 
    parent = Organism(tg.size,INITIAL_GENES) #calling Organism class, and passing the target size and initial gene pool size as params
    

    
    score=fitness(tg,parent.drawImage())

    while True:
        
        print("Generation {} - Score {}".format(generation,score))
        #f.write("Generation {} - Score {}\n".format(generation,score))
  
        if generation % GENERATIONS_PER_IMAGE == 0:
            parent.drawImage().save(os.path.join("Solutions","{}.jpeg".format(generation)))
            
        generation += 1
        p = multiprocessing.Pool(cores)
        
        """
        This is where the genetic algo really starts.
        We will first start with making a children and a ss_scores array (idk why ss, it sounds cool)
        """
        children=[]
        ss_score=[]

        """
        Next, we will basically mutate and check fitness, then save to results, unless interrupted by the keyboard
        """

        try:
            results = groupMutate(parent,POP_PER_GEN-1,p)
        except KeyboardInterrupt:
            print ('Sayonara!')
            p.close()
            return

        """
        Now we will do 2 things to the children and the ss_scores arrays:
        save parents and score to those 2, incase the parents are better than the children
        """
        children.append(parent)
        ss_score.append(score)
    
        """
        Then we will put new children and new scores in those
        """
        newScores,newChildren = zip(*results)

        children.extend(newChildren)
        ss_score.extend(newScores)

        """
        Finally, we sort them, and pick the best to become the new parents (and log in the best in the scores too)
        """
    
    
        winners = sorted(zip(children,ss_score),key=lambda x: x[1])
        #lambda here creates a memroy space in the area of calling, which makes the execution time "blazingly fast", quoting pranjal :)
    
    
        parent,score = winners[0]
    
        
        """
        Now, these parents will go through mutation and give new children
        """

        #this is becuase at one point, too many files are open, since we are opening a pool inside a loop, then not shutting it down

        p.terminate()


if __name__ == "__main__":
    cores = max(1,(multiprocessing.cpu_count()//2)+1)
    
    run(cores)
