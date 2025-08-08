"""Author: Dr. Joshua Thomas
thomas.joshd@gmail.com
thomasjd@alfred.edu

The 24 hour display has black numbers on the outside for local time.

The blue numbers on the inner ring change on their own so that the meridian
(indicated by the hour hand) is pointing to both the current right ascension of
the meridian (local sidereal time) and the local civil time.

The purple and blue hour hands always move together and is color coordinated
with the digital displays at the bottom.

The red hour hand indicates the UT time on the black ring of numbers, and
corresponds to the red UT digital display.

The thin gray lines perpendicular to the purple/blue hour hands indicates 6
hours of hour angle, approximately the horizon at the celestial equator.

The planets are indicated by their astronomical symbols, they are approximately
color coded red for Mars, Jupiter and Saturn are the same color as "giant"
planets and Neptune and Uranus are blue for "ice giants". Their location is
their right ascension, so it can be read from the blue set of numbers of the
dial.  Their distances from the center (earth) follow a geocentric-type
approach, the distances are not scaled and are set a fixed values that looked
nice. Venus and Mercury are black when inferior to the sun, and red when
superior to the sun.

The sunset/sunrise times are color coordinated with marks on the dial and the
nighttime hours are shaded.

The moon phase can be inferred from the relative position of the Sun, Earth, and
 Moon.  The Earth is at the center of the dial.  Since this is a clock, the
 moon moves clockwise in right ascension. To aid in interpreting phase 1st and
 3rd quarters are marked, new moon is of course when the moon is between the
 sun and earth.


"""
UPDATED="06-AUG-2025"
version="0.9"
#------------------------------------
#Site Parameters Change these to display correct sidereal time.
#Note your system time and timezone must match this information.
#------------------------------------
# sitename = "Stull Observatory" #your desired latitude
# latitude = 42.249999 # your latitue in decimal degrees
# longitude = -77.783302 # your longitude in decimal degrees West is negative
#------------------------------------

import math
import tkinter as tk
from tkinter import filedialog as fd
from astropy.time import Time
import astropy as ap
import astropy.units as u
from datetime import datetime,timezone,timedelta
from suntime import Sun, SunTimeException
from astroplan import moon_illumination,Observer

#mute warnings
import warnings
warnings.filterwarnings("ignore")

#some regularly used constanc
pi12=math.pi/12
pi2=math.pi/2
pi24=math.pi/24

class App:
    def __init__(self,master):
        self.bckgrnd='white' #background color
        self.fg1='purple' #foreground color 1
        self.fg2='black' #foreground color 2
        self.fontsize=16 #fontsize and WIDTH are inter-related
        self.font="Courier" #this should remain a fixed-width font
        self.WIDTH=420
        self.fontsize_def=16
        self.WIDTH_def=420
        latitude = 42.249999 # your latitude in decimal degrees
        longitude = -77.783302 # your longitude in decimal degrees West is negative
        self.lat = "%sd"%latitude
        self.lon = "%sd"%longitude
        self.latf = latitude
        self.lonf = longitude
        self.latf_def=latitude
        self.lonf_def=longitude
        # self.sethour=0 #this is from a texting version of the code to manually change time.  Not actively used.
        self.moonphase=0
        self.moonphaseold=0
        self.sitename="Stull Observatory"
        self.sitename_def=self.sitename
        self.E1=0 #entry boxes for setting the site.
        self.E2=0
        self.E3=0
        self.E4=0
        self.E5=0
        self.loadprefs()

        self.master=master
        self.master.title("Observatory Clock, Version %s"%str(version))
        self.gencanvas()


        self.time_update() #runs the initial clock generation
        self.bindings() #initialize keybindings


        menu = tk.Menu(master)
        master.config(menu=menu)

        filemenu = tk.Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Set Preferences",command=self.setobs)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self._quit)

        about = tk.Menu(menu)
        menu.add_cascade(label="About", menu=about)
        about.add_command(label="About", command=self.about)



    def bindings(self):
        #keyboard shortcuts
        self.master.bind('q', lambda event: self._quit())

    def gencanvas(self):

        self.HEIGHT=self.WIDTH #force square for circular clock.
        self.WIDTH2=self.WIDTH/2  #this is done alot, so make it quicker on the computer.
        self.HEIGHT2=self.HEIGHT/2

        #window gemoetry
        self.master.geometry('%sx%s'%(int(self.WIDTH+self.WIDTH/2),int(self.HEIGHT+self.HEIGHT/2)))
        self.master.configure(background="white")
        # self.master.attributes('-zoomed', True)

        # clock canvas
        self.header = tk.Label(self.master, font=(self.font, self.fontsize, "bold"), fg=self.fg1,bg=self.bckgrnd)
        self.freindly = tk.Label(self.master, font=(self.font, self.fontsize, "bold"), fg=self.fg1,bg=self.bckgrnd)
        self.prefix = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg1,bg=self.bckgrnd)

        self.mil = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg1,bg=self.bckgrnd, justify=tk.LEFT)
        self.localdatedisp = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg1,bg=self.bckgrnd, justify=tk.LEFT)
        self.lastdisp = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg="blue",bg=self.bckgrnd, justify=tk.LEFT)

        self.header2 = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg2,bg=self.bckgrnd, justify=tk.LEFT)
        self.header2.config(text="UTC")
        self.utdisp = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg="red",bg=self.bckgrnd, justify=tk.LEFT)
        self.utdatedisp = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg2,bg=self.bckgrnd, justify=tk.LEFT)
        self.jddisp =  tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg2,bg=self.bckgrnd, justify=tk.LEFT)
        self.mjddisp = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg2,bg=self.bckgrnd, justify=tk.LEFT)
        self.gastdisp = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg=self.fg2,bg=self.bckgrnd, justify=tk.LEFT)

        self.sr = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg="green",bg=self.bckgrnd, justify=tk.LEFT)
        self.ss = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg="green",bg=self.bckgrnd, justify=tk.LEFT)
        self.moonillumination = tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg="black",bg=self.bckgrnd, justify=tk.LEFT)

        self.textboxlabel=tk.Label(self.master, font=(self.font, self.fontsize, "normal"), fg="black",bg=self.bckgrnd, justify=tk.LEFT)
        self.canvas = tk.Canvas(self.master, width=self.WIDTH, height=self.HEIGHT, bg=self.bckgrnd, highlightthickness=0)

        self.header.grid(row=0,column=0,columnspan=2)

        self.canvas.grid(row=1,column=0,columnspan=2)
        self.freindly.grid(row=2,column=0,columnspan=2)

        self.mil.grid(row=4,column=0, sticky=tk.W)
        self.lastdisp.grid(row=5,column=0, sticky=tk.W)

        self.utdisp.grid(row=4,column=1, sticky=tk.W)
        self.gastdisp.grid(row=5,column=1, sticky=tk.W)

        self.jddisp.grid(row=6,column=0, sticky=tk.W)
        self.mjddisp.grid(row=6,column=1, sticky=tk.W)

        self.sr.grid(row=7,column=0, sticky=tk.W)
        self.ss.grid(row=7,column=1, sticky=tk.W)

        self.moonillumination.grid(row=8,column=0, sticky=tk.W)
        # self.prefix.grid(row=9,column=0,columnspan=2)

    # Update clock display time
    def time_update(self):
        #gnerate all the times based off the system clock and system timzeone.
        #also prints the texts parts of the time.
        self.canvas.delete("all")

        self.header.config(text="%s"%self.sitename)
        t=Time.now()
        self.local=datetime.now()#+timedelta(hours=self.sethour)
        LT=self.local.strftime("%H:%M")
        LD=self.local.strftime("%Y%m%d")

        self.ut=Time(t,location=(self.lon, self.lat))#+timedelta(hours=self.sethour)

        ut_hour=float(self.ut.utc.strftime("%H"))

        site = Observer(longitude=self.lonf*u.deg, latitude=self.latf*u.deg, elevation=0*u.m)
        self.moonphase=site.moon_illumination(self.ut)

        self.get_delta_T(self.local.hour,ut_hour)
        self.riseset()
        # ut = Time(datetime.now(tz=timezone.utc), scale='utc')
        JD=self.ut.jd
        MJD=self.ut.mjd
        UT=self.ut.utc.strftime("%H:%M")
        UD=self.ut.utc.strftime("%Y%m%d")
        GAST=self.ut.sidereal_time('apparent', 'greenwich')
        LAST=self.ut.sidereal_time('apparent')
        GAST=self.sidereal_split(str(GAST))
        LAST=self.sidereal_split(str(LAST))

        prefixl=self.ut.strftime("%Y%m%d")


        freindlyt=self.local.strftime("%A, %d. %B %Y %I:%M%p")
        self.freindly.config(text=freindlyt)
        self.prefix.config(text="Fileprefix:  "+prefixl)

        self.mil.config(          text="LOCAL: "  +LT)
        self.lastdisp.config(     text="LST : "  +f'{LAST[0]:02}'+':'+f'{LAST[1]:02}')

        self.utdisp.config(       text="UT  : "  +UT)
        self.gastdisp.config(     text="GST: "  +f'{GAST[0]:02}'+':'+f'{GAST[1]:02}')
        self.jddisp.config(       text="JD   : "  +'%0.4f'%JD)
        self.mjddisp.config(      text="MJD : "  +'%0.4f'%MJD)
        try:
            self.sr.config(           text="\u2609RISE: "  +'%2s:%2s'%(self.srhour,self.today_sr.strftime('%M')))
            self.ss.config(           text="\u2609SET: "  +'%2s:%2s'%(self.sshour,self.today_ss.strftime('%M')))
        except:
            pass
        if self.moonphase > self.moonphaseold:
            ww="waxing"
        elif self.moonphase < self.moonphaseold:
            ww="waning"
        else:
            ww=""

        self.moonillumination.config(text=u"Moon Illumination: %0.1f%% %s"%(self.moonphase*100,ww))

        self.clock_update() #calls the amazing astronomical clock drawing.
        self.freindly.after(20000, self.time_update) #updates every 20000 milliseconds, arbitrairly chosen to not have to redraw the screen as much.

    def draw_object(self,angle,stdelta,radius,symbol,color="red",font="times",fontsize=16):
        hour_angle = angle/15* pi12 +stdelta* pi12-pi2 #takes angle in degrees
        hour_x = self.WIDTH2 + radius * self.WIDTH2 * math.cos(hour_angle)
        hour_y = self.HEIGHT2 + radius * self.HEIGHT2 * math.sin(hour_angle)
        self.canvas.create_text(hour_x, hour_y, text=symbol, font=(self.font, self.fontsize),fill=color)

    def draw_face_lines(self,font="times",fontsize=16):
        # Draw clock face
        self.canvas.create_oval(0, 0, self.WIDTH, self.HEIGHT, outline="purple", width=3)

        # Draw hour numbers
        for i in range(24):
            angle = i * pi12 - pi2
            x = self.WIDTH2 + 0.92 * self.WIDTH2 * math.cos(angle)
            y = self.HEIGHT2 + 0.92 * self.WIDTH2 * math.sin(angle)

            # if self.sethour==0:
            self.canvas.create_text(x, y, text=str(i), font=(self.font, self.fontsize),fill="black")
            # else:
            #     self.canvas.create_text(x, y, text=str(i), font=(self.font, self.fontsize),fill="red")

        # Draw hour lines
        for i in range(48):
            angle = i * pi24 - pi2
            x1 = self.WIDTH2 + 0.81 * self.WIDTH2 * math.cos(angle)
            y1 = self.HEIGHT2 + 0.81 * self.HEIGHT2 * math.sin(angle)
            x2 = self.WIDTH2 + 0.84 * self.WIDTH2 * math.cos(angle)
            y2 = self.HEIGHT2 + 0.84 * self.HEIGHT2 * math.sin(angle)
            if i % 2 == 0:
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=3)
            else:
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=1)

    def draw_st(self,sti,stangle,font="times",fontsize=12):
        # Draw ST hour numbers, a rotating dail of right ascension numbers
        st=sti[0]+sti[1]/60.+sti[2]/3600.
        for i in range(24):
            angle=(stangle-sti[1]/60*pi12)+i*pi12
            x = self.WIDTH2 + 0.74 * self.WIDTH2 * math.cos(angle)
            y = self.HEIGHT2 + 0.74 * self.WIDTH2 * math.sin(angle)

            l=int(st+i)
            if l < 24:
                self.canvas.create_text(x, y, text=str(l), font=(self.font, self.fontsize),fill="blue")
            else:
                self.canvas.create_text(x, y, text=str(l%24), font=(self.font, self.fontsize),fill="blue")
        # Draw hour lines for Right ascension/LST
        for i in range(24):
            angle=(stangle-sti[1]/60*pi12)+i*pi12
            x1 = self.WIDTH2 + 0.65 * self.WIDTH2 * math.cos(angle)
            y1 = self.HEIGHT2 + 0.65 * self.HEIGHT2 * math.sin(angle)
            x2 = self.WIDTH2 + 0.67 * self.WIDTH2 * math.cos(angle)
            y2 = self.HEIGHT2 + 0.67 * self.HEIGHT2 * math.sin(angle)
            # if i % 2 == 0:
            self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)
            # else:
            #     self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=1)


    def get_delta_ST(self,LAST):
        st=float(LAST[0])+LAST[1]/60.+LAST[2]/3600.
        l=float(self.local.hour)+self.local.minute/60.+self.local.second/3600.
        return(l-st)

    def get_delta_T(self,hour,ut_hour):
        if hour > ut_hour:
            self.deltat=hour%12-int(ut_hour+12)
        else:
            self.deltat=hour-int(ut_hour)


    def riseset(self):
        #gets the sunrise and sunset times
        bsun = Sun(self.latf, self.lonf)
        try:
            self.today_sr = bsun.get_sunrise_time(self.local)
            self.today_ss = bsun.get_sunset_time(self.local)
            self.srhour=(int(self.today_sr.strftime('%H'))+self.deltat)%24 #needed to convert from UT to localtime on 24hr
            self.sshour=(int(self.today_ss.strftime('%H'))+self.deltat+24)%24 #needed to convert from UT to localtime on 24hr
        except:
            self.today_sr=0
            self.today_ss=0
            self.srhour=0
            self.sshour=0

    def draw_sunrise_sunset(self):
        # Draw sunrise
        try:
            hour_angle_sr = (self.srhour + int(self.today_sr.strftime('%M'))/60) * pi12 - pi2
            self.sunrise_ang=math.degrees(hour_angle_sr)
            hour_angle_ss = (self.sshour + int(self.today_ss.strftime('%M'))/60) * pi12 - pi2
            self.sunset_ang=math.degrees(hour_angle_ss)
            night=(self.sunrise_ang-self.sunset_ang)%360
            # print(self.sunrise_ang,night)
            self.canvas.create_arc(2, 2, self.WIDTH, self.HEIGHT, start=-self.sunrise_ang,extent=night,fill="#eeeeee")

            x1 = self.WIDTH2 + 0.5 * self.WIDTH2 * math.cos(hour_angle_sr)
            y1 = self.HEIGHT2 + 0.5 * self.HEIGHT2 * math.sin(hour_angle_sr)
            x2 = self.WIDTH2 + 0.7 * self.WIDTH2 * math.cos(hour_angle_sr)
            y2 = self.HEIGHT2 + 0.7 * self.HEIGHT2 * math.sin(hour_angle_sr)
            self.canvas.create_line(x1, y1, x2, y2, fill="green", width=2)

            # Draw sunset

            x1 = self.WIDTH2 + 0.5 * self.WIDTH2 * math.cos(hour_angle_ss)
            y1 = self.HEIGHT2 + 0.5 * self.HEIGHT2 * math.sin(hour_angle_ss)
            x2 = self.WIDTH2 + 0.7 * self.WIDTH2 * math.cos(hour_angle_ss)
            y2 = self.HEIGHT2 + 0.7 * self.HEIGHT2 * math.sin(hour_angle_ss)
            self.canvas.create_line(x1, y1, x2, y2, fill="green", width=2)
        except:
            pass

    def draw_mooncross(self,sun,stdelta):
        #Draw moon phase cross
        #new
        sun_angle = sun.ra.value/15* pi12 +stdelta* pi12-pi2
        hour_x = self.WIDTH2 + 0.15 * self.WIDTH2 * math.cos(sun_angle)
        hour_y = self.HEIGHT2 + 0.15 * self.HEIGHT2 * math.sin(sun_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="black", width=1)
        # self.draw_object(sun.ra.value,stdelta,0.15,u"0",color="black")
        #full
        sun_angle = sun.ra.value/15* pi12 +stdelta* pi12+pi2
        hour_x = self.WIDTH2 + 0.15 * self.WIDTH2 * math.cos(sun_angle)
        hour_y = self.HEIGHT2 + 0.15 * self.HEIGHT2 * math.sin(sun_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="black", width=1)
        #1st
        sun_angle = sun.ra.value/15* pi12 +stdelta* pi12
        hour_x = self.WIDTH2 + 0.15 * self.WIDTH2 * math.cos(sun_angle)
        hour_y = self.HEIGHT2 + 0.15 * self.HEIGHT2 * math.sin(sun_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="black", width=1)
        self.draw_object(sun.ra.value+90,stdelta,0.17,u"1",color="black")
        #3rd
        sun_angle = sun.ra.value/15* pi12 +stdelta* pi12-math.pi
        hour_x = self.WIDTH2 + 0.15 * self.WIDTH2 * math.cos(sun_angle)
        hour_y = self.HEIGHT2 + 0.15 * self.HEIGHT2 * math.sin(sun_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="black", width=1)
        self.draw_object(sun.ra.value-90,stdelta,0.17,u"3",color="black")


    def draw_hourhand(self):
        # Draw hour hand
        hour_angle = (self.local.hour + self.local.minute/60) * pi12 - pi2
        hour_x = self.WIDTH2 + 0.9 * self.WIDTH2 * math.cos(hour_angle)
        hour_y = self.HEIGHT2 + 0.9 * self.HEIGHT2 * math.sin(hour_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="purple", width=4,arrow='last')

    def draw_horizon(self):
        #draw the "effective" horizon at + and - 6 hours from the merdian (hour hand)
        # Draw perpendicular 1
        hour_angle = (self.local.hour + self.local.minute/60) * pi12
        hour_x = self.WIDTH2 + 0.7 * self.WIDTH2 * math.cos(hour_angle)
        hour_y = self.HEIGHT2 + 0.7 * self.HEIGHT2 * math.sin(hour_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="grey", width=1)
        # Draw  perpendicular 2
        hour_angle = (self.local.hour + self.local.minute/60) * pi12 - pi2-pi2
        hour_x = self.WIDTH2 + 0.7 * self.WIDTH2 * math.cos(hour_angle)
        hour_y = self.HEIGHT2 + 0.7 * self.HEIGHT2 * math.sin(hour_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="grey", width=1)

    def draw_uthour(self,ut_hour):
        # Draw UT hour hand
        hour_angle = (ut_hour + self.local.minute/60) * pi12 - pi2
        hour_x = self.WIDTH2 + 0.8 * self.WIDTH2 * math.cos(hour_angle)
        hour_y = self.HEIGHT2 + 0.8 * self.HEIGHT2 * math.sin(hour_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="red", width=4,arrow='last')

    def draw_LSThour(self,stangle):
        # Draw LAST hour hand
        hour_angle = stangle #* pi12 - pi2
        hour_x = self.WIDTH2 + 0.6 * self.WIDTH2 * math.cos(hour_angle)
        hour_y = self.HEIGHT2 + 0.6 * self.HEIGHT2 * math.sin(hour_angle)
        self.canvas.create_line(self.WIDTH2, self.HEIGHT2, hour_x, hour_y, fill="blue", width=5,arrow='last')


    def draw_moonsym(self,moon,stdelta):
        #admust the greyscale level based on the phave.
        if self.moonphase < 0.125 and self.moonphase > 0.875:
            #new
            self.draw_object(moon.ra.value,stdelta,0.1,u"\u263E",color="#cccccc")
        elif self.moonphase > 0.125 and self.moonphase < 0.375:
            #wax quarter
            self.draw_object(moon.ra.value,stdelta,0.1,u"\u263E",color="#666666")
        elif self.moonphase > 0.375 and self.moonphase < 0.625:
            #full
            self.draw_object(moon.ra.value,stdelta,0.1,u"\u263E",color="#222222")
        elif self.moonphase > 0.625 and self.moonphase < 0.875:
            #wanning quarter
            self.draw_object(moon.ra.value,stdelta,0.1,u"\u263E",color="#666666")
        else:
            self.draw_object(moon.ra.value,stdelta,0.1,u"\u263E",color="black")

    def clock_update(self):
        #Draw Astroclock

        ut_hour=float(self.ut.utc.strftime("%H"))

        LAST=self.ut.sidereal_time('apparent')
        LAST=self.sidereal_split(str(LAST))
        stdelta=self.get_delta_ST(LAST)

        stangle=float(LAST[0]) + float(LAST[1])/60.#-stdelta+nightlength
        stangle = stangle * pi12 - pi2 +stdelta* pi12

        #Get ephemeris for solar system objects
        moon=ap.coordinates.get_body("moon",self.ut)
        sun=ap.coordinates.get_body("sun",self.ut)
        mercury=ap.coordinates.get_body("mercury",self.ut)
        venus=ap.coordinates.get_body("venus",self.ut)
        mars=ap.coordinates.get_body("mars",self.ut)
        jupiter=ap.coordinates.get_body("jupiter",self.ut)
        saturn=ap.coordinates.get_body("saturn",self.ut)
        uranus=ap.coordinates.get_body("uranus",self.ut)
        neptune=ap.coordinates.get_body("neptune",self.ut)

        try:
            nightlength=self.srhour+24-self.sshour
        except:
            nightlength=0

        self.draw_sunrise_sunset()
        self.draw_st(LAST,stangle)
        self.draw_face_lines(font=self.font,fontsize=self.fontsize)
        self.draw_mooncross(sun,stdelta)
        self.draw_hourhand()
        self.draw_horizon()
        self.draw_uthour(ut_hour)
        self.draw_LSThour(stangle)
        self.draw_moonsym(moon,stdelta)

        #draw the solar system objects
        self.draw_object(sun.ra.value,stdelta,0.3,u"\u2609",color="black")
        if mercury.distance.value<sun.distance.value:
            self.draw_object(mercury.ra.value,stdelta,0.25,u"\u263F",color="black")
        else:
            self.draw_object(mercury.ra.value,stdelta,0.35,u"\u263F",color="#b22222")
        if venus.distance.value<sun.distance.value:
            self.draw_object(venus.ra.value,stdelta,0.2,u"\u2640",color="black")
        else:
            self.draw_object(venus.ra.value,stdelta,0.4,u"\u2640",color="#b22222")
        self.draw_object(mars.ra.value,stdelta,0.5,u"\u2642",color="#8b0000")
        self.draw_object(jupiter.ra.value,stdelta,0.55,u"\u2643",color="grey")
        self.draw_object(saturn.ra.value,stdelta,0.58,u"\u2644",color="grey")
        self.draw_object(uranus.ra.value,stdelta,0.62,u"\u26E2",color="#00bfff")
        self.draw_object(neptune.ra.value,stdelta,0.67,u"\u2646",color="#00bfff")

    def strdelta(self,delta):
        secs=delta.total_seconds()
        days, rem = divmod(secs, 86400)  # Seconds per day: 24 * 60 * 60
        hours, rem = divmod(rem, 3600)  # Seconds per hour: 60 * 60
        mins, secs = divmod(rem, 60)
        H="{:02d}".format(int(hours))
        M="{:02d}".format(int(mins))
        S="{:02d}".format(int(secs))
        return H+":"+M+":"+S

    def sidereal_split(self,time):
        # function to reformat the sidereal time
        st=[]
        h=str(time).split('h')
        st.append(h[0])
        m=h[1].split('m')
        st.append(m[0])
        s=m[1].split('s')
        # print(s)
        st.append(s[0])
        return (int(h[0]),int(m[0]),float(s[0]))

    def _quit(self):
        self.master.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate
        self.master.quit()     # stops mainloop
        root.quit()


    def setobs(self):
        t=tk.Toplevel(self.master,height=600,width=80)
        t.wm_title("Observatory")
        tk.Label(t,text="Set Observatory Location\n\nPlease note this information must match a coordinate within your computer's set timezone.\n\n").pack()
        tk.Label(t,text="Display Name:").pack()

        self.N=tk.StringVar()
        self.E1=tk.Entry(t,width=50,text=self.N)
        self.E1.pack()
        self.N.set(self.sitename)

        self.L1=tk.StringVar()
        tk.Label(t,text="Latitude:").pack()
        self.E2=tk.Entry(t,width=50,text=self.L1)
        self.E2.pack()
        self.L1.set(str(self.latf))

        self.L2=tk.StringVar()
        tk.Label(t,text="Longitude:").pack()
        self.E3=tk.Entry(t,width=50,text=self.L2)
        self.E3.pack()
        self.L2.set(str(self.lonf))

        tk.Label(t,text="\n\nThe settings below requrie a restart.").pack()
        tk.Label(t,text="Set desired fontsize, default is 16pt:").pack()
        self.F=tk.StringVar()
        self.E4=tk.Entry(t,width=50,text=self.F)
        self.E4.pack()
        self.F.set(self.fontsize)

        tk.Label(t,text="\n\nClock Size, default is 420px:").pack()
        self.W=tk.StringVar()
        self.E5=tk.Entry(t,width=50,text=self.W)
        self.E5.pack()
        self.W.set(self.WIDTH)


        set_button = tk.Button(t, text="Set", command=self.siteupdate)
        set_button.pack(pady=10)

        reset_button = tk.Button(t, text="Default Values", command=self.setdef)
        reset_button.pack(pady=10)

    def siteupdate(self):
        self.sitename=self.E1.get()
        self.latf=float(self.E2.get())
        self.lonf=float(self.E3.get())
        self.time_update()
        self.saveprefs()

    def loadprefs(self):
        try:
            dataout=open('settings.par')
            for i,line in enumerate(dataout):
                if i == 0 :
                    self.sitename=line.strip()
                elif i == 1 :
                    self.latf=float(line.strip())
                elif i == 2 :
                    self.lonf=float(line.strip())
                elif i == 3 :
                    self.fontsize=int(line.strip())
                elif i == 4 :
                    self.WIDTH=int(line.strip())
            dataout.close()
        except:
            pass

    def saveprefs(self):
        try:
            dataout=open('settings.par','w')
            dataout.write('%s\n'%(self.sitename))
            dataout.write('%s\n'%(self.latf))
            dataout.write('%s\n'%(self.lonf))
            dataout.write('%s\n'%(self.E4.get()))
            dataout.write('%s\n'%(self.E5.get()))
            dataout.close()

        except:
            print("failed to save preferences")



    def setdef(self):
        self.sitename=self.sitename_def
        self.latf=self.latf_def
        self.lonf=self.lonf_def
        self.N.set(self.sitename_def)
        self.L1.set(self.latf_def)
        self.L2.set(self.lonf_def)
        self.F.set(self.fontsize_def)
        self.W.set(self.WIDTH_def)
        self.time_update()

    def about(self):
        t=tk.Toplevel(self.master,height=600,width=80)
        t.wm_title("About")
        tk.Label(t,text="Version %s"%version).pack()
        tk.Label(t,text="Last Updated %s"%UPDATED).pack()
        tk.Label(t,text="Author: Dr. Joshua Thomas\nthomas.joshd@gmail.com\n thomasjd@alfred.edu\n\nThe 24 hour display has black numbers on the outside for local time.\n\nThe blue numbers on the inner ring change on their own so that the meridian \n(indicated by the hour hand) is pointing to both the current right ascension of \nthe meridian (local sidereal time) and the local civil time.\n\nThe purple and blue hour hands always move together and is color coordinated \nwith the digital displays at the bottom.\n\nThe red hour hand indicates the UT time on the black ring of numbers, and \ncorresponds to the red UT digital display.\n\nThe thin gray lines perpendicular to the purple blue hour hands indicates 6 \nhours of hour angle, approximately the horizon at the celestial equator.\n\nThe planets are indicated by their astronomical symbols, they are approximately \ncolor coded red for Mars, Jupiter and Saturn are the same color as giant \nplanets and Neptune and Uranus are blue for ice giants. Their location is \ntheir right ascension, so it can be read from the blue set of numbers of the \ndial.  Their distances from the center (earth) follow a geocentric-type \napproach, the distances are not scaled and are set a fixed values that looked \nnice. Venus and Mercury are black when inferior to the sun, and red when \nsuperior to the sun.\n\nThe sunset/sunrise times are color coordinated with marks on the dial and the \nnighttime hours are shaded.\n\nThe moon phase can be inferred from the relative position of the Sun, Earth, and\n Moon.  The Earth is at the center of the dial.  Since this is a clock, the \n moon moves clockwise in right ascension. To aid in interpreting phase 1st and \n3rd quarters are marked, new moon is of course when the moon is between the \nsun and earth.").pack()


#Begin GUI

root = tk.Tk() #main GUI window
program=App(root)
root.protocol("WM_DELETE_WINDOW", program._quit)
root.mainloop() #lets the GUI run
