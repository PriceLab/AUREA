from Tkinter import *
import traceback, tkMessageBox
import Tkconstants, tkFileDialog
import AUREA
import AUREA.GUI.AUREAPage as AUREAPage
from AUREA.parser.SettingsParser import *
import os.path
import shutil
import sys
import platform
class AUREAApp(Frame):
    def __init__(self, root, controller):
        
        root.report_callback_exception = self.report_callback_exception
        Frame.__init__(self, root)
        root.rowconfigure( 0, weight = 1 )
        root.columnconfigure( 0, weight = 1 )
        self.grid(sticky=W+E+N+S )
        self.err_disp = False#only display one error
        self.root = root
        self.root.title( "AUREA - Adaptive Unified Relative Expression Analyser")
        self.controller = controller
        self.curr_page = None
        self.pages = []
        self._initApp()
        self.rowconfigure( 1, weight = 1 )
        self.columnconfigure( 1, weight = 1 )

    def _initApp(self):
        """
        Set up all of the App Frame components
        """
        self.menu = AUREAMenu(self)
        self.remote = AUREARemote(self)
        self.buttonList = self.remote.buttonList
        self.root.config(menu = self.menu)
        self.status = StatusBar(self)
        self.AppTitle = StringVar()
        
        self.AppTitleLabel = Label(self, textvariable=self.AppTitle)
        import tkFont
        font = tkFont.Font(font=self.AppTitleLabel['font'])
        font.config(size=font.cget('size')*2, weight='bold', underline=1)
        self.AppTitleLabel['font'] = font
        self.AppTitle.set("Data Summary")
        self.AppTitleLabel.grid(row=0, column=0, columnspan=2, sticky=N+W+E+S)
        self.grid_columnconfigure(1,minsize=205)
        self.remote.grid(row=1, column=0, sticky=N+E+W)
        self.initPages()
        self.displayPage('Home')
        numcolumns, numrows = self.grid_size()
        self.status.grid(row=numrows,column=0, columnspan=numcolumns, sticky=W+E+S)
        self.update_idletasks()
       

    def setAppTitle(self, title):
        self.AppTitle.set(title)
       
    def initPages(self):
        self.pages.append(AUREAPage.HomePage(self))
        self.pages.append(AUREAPage.ImportDataPage(self))
        self.pages.append(AUREAPage.ClassDefinitionPage(self))
        self.pages.append(AUREAPage.LearnerSettingsPage(self))
        self.pages.append(AUREAPage.TrainClassifiers(self))
        self.pages.append(AUREAPage.TestClassifiers(self))
        self.pages.append(AUREAPage.EvaluateClassifiers(self)) 

    def displayPage(self, page_id):
        self.status.clear()
        if self.curr_page:
            self.curr_page.clearPage()
            self.curr_page.grid_forget()
            self.curr_page = None
        for page in self.pages:
            if page.id == page_id:
                page.setUpPage()
                page.drawPage()
                self.curr_page = page
                break
        self.curr_page.grid(column=1, row=1,sticky=N+S+E+W)
        self.curr_page.rowconfigure( 1, weight = 1 )
        self.curr_page.columnconfigure( 1, weight = 1 )
        self.root.update_idletasks()

    def next(self):
        try:
            next = self.curr_page.next()
        except AUREAPage.ImplementationError as e:
            print e.msg

        if next:
            self.displayPage(next)

    def prev(self):
        try:
            prev = self.curr_page.prev()
        except AUREAPage.ImplementationError as e:
            print e.msg

        if prev:
            self.displayPage(prev)


    def report_callback_exception(self, *args):
        """
        displays exceptions
        TYVM : http://stackoverflow.com/questions/4770993/silent-exceptions-in-python-tkinter-should-i-make-them-louder-how
        """
        if self.err_disp:
            return
        try:#clear buttons
            self.remote.disableAllButtons()
        except Exception, e:
            print e
            
        err = traceback.format_exception(*args)
        msg = "An Error has occurred."
        t = Toplevel(self)
        t.title("AUREA Error!!!!!")
        Label(t,text=msg).pack()
        import os
        errmsg = 'Please copy this error and go to https://github.com/JohnCEarls/AUREAPackage/issues to report it'+ os.linesep
        errmsg += '(You may have to use Control-C or Apple-C to copy.)'+ os.linesep
        errmsg +=os.linesep.join(err)
        errBox = Text(t,wrap=WORD)
        errBox.pack()
        errBox.insert(END, errmsg) 
        self.err_disp = True


class StatusBar(Frame):
    """
    Note the statusbar is a child of the root
    """
    def __init__(self, master):
        Frame.__init__(self, master)
        self.label = Label(self, bd=1, relief=SUNKEN, anchor=W)
        self.label.pack(fill=X)

    def set(self, format, *args):
        self.label.config(text=format % args)
        self.label.update_idletasks()

    def clear(self):
        self.label.config(text="")
        self.label.update_idletasks()               
        

class AUREARemote(Frame):
    """
    This frame acts as the remote control for the gui.
    """
    #Dependency enum, these should be static
    DataImport = 0
    NetworkImport = 1
    ClassCreation = 2
    TrainDirac = 3
    TrainTSP = 4
    TrainTST = 5
    TrainKTSP = 6
    TrainAdaptive = 7
    TrainAny = 8#specialCase
    #end enum
    NumStates = 9 #number of states in dependencies
    def __init__(self, master):
        """
        Builds the left side controller of AUREA
        master - the AUREAApp Frame
        """
        Frame.__init__(self, master, width=200)
        self.m = master
        aa=AUREARemote
        self.depGraph = [[0 for x in range(aa.NumStates)] for y in range(aa.NumStates)]
        self.setNavDependencies()
        self.buildNav()
        self.buildDependencyGraph()
        self.layoutNav()
        self.stateChange()

    def buildDependencyGraph(self):
        """
        The dependency graph stores direct dependencies
        """
        def depends(A,B):
            for x in A:
                for y in B:
                    self.depGraph[x][y] = 1
        aa= AUREARemote

        depends([aa.TrainAdaptive,aa.TrainDirac,aa.TrainKTSP,aa.TrainTSP,aa.TrainTST], [aa.ClassCreation])
        depends([aa.TrainAdaptive, aa.TrainDirac],[aa.NetworkImport])
        depends([aa.ClassCreation], [aa.DataImport])

    def getDependents(self, dependency):
        return [g[dependency] for g in self.depGraph]


    def getDepVector(self, dependencies):
        """
        Given a list of dependencies(A), return a list of 1s and 0s
        showing associated dependencies(B)
        Where A depends on B
        """
        def setDep(dvector, dependency):
            dvector[dependency] = 1
        def traverse(node):
            traversal = [node]
            for i,x in enumerate(self.depGraph[node]):
                if x == 1:
                    traversal.append(i)
                    for j in traverse(i):
                        traversal.append(j)
            return traversal
        aa=AUREARemote
        dvec = [0 for x in range(aa.NumStates)]
        #basically unioning all dependency paths
        for dep in dependencies:
            t = traverse(dep)
            for node in t:
                setDep(dvec, node)
        
        return dvec

    def dependenciesSatisfied(self,currState, depVector):
        """
        Given the current state and the dependency vector
        Return True if all dependencies have been satisfied
        """
        aa = AUREARemote

        if depVector[aa.TrainAny] == 1:
            #special case for when any LA has run
            for d in [self.getDepVector([x]) for x in [aa.TrainDirac, aa.TrainTSP, aa.TrainTST, aa.TrainKTSP, aa.TrainAdaptive]]:
                if self.dependenciesSatisfied(currState, d):
                    return True
            return False

        for i, on in enumerate(currState):
            if depVector[i] == 1 and on != 1:
                return False
        return True

    def stateChange(self):
        """
        Enables or disables buttons based on their dependencies
        and the current state of controller
        """
        for i,button in enumerate(self.buttonList):
            dvec = self.getDepVector(self.navDep[i])
            if self.dependenciesSatisfied(self.m.controller.dependency_state,dvec ):
               button.configure(state=NORMAL)
            else:
               button.configure(state=DISABLED)

    def disableAllButtons(self):
        """
        Disables all buttons
        """
        for button in self.buttonList:
            button.configure(state=DISABLED)



    def setNavDependencies(self):
        """
        Maps between buttons and dependencies
        """
        aa = AUREARemote
        self.navDep = []
        #home
        self.navDep.append([])
        #import data
        self.navDep.append([])
        #class definition
        self.navDep.append([aa.DataImport])
        #Learner Settings
        self.navDep.append([])
        #Train Classifiers
        self.navDep.append([aa.ClassCreation])
        #Test Classifiers
        self.navDep.append([aa.TrainAny])
        #Evaluate Performance
        self.navDep.append([aa.ClassCreation])

    def buildNav(self):
        """
        Create button objects
        """
        import os
        home_message = "Home:"+ 2*os.linesep + "View a summary of the current state of AUREA."
        import_message = "Import Data:"+2*os.linesep+ "Import the data on which to base the models." + os.linesep + "Browse for or download the data files for training and classification." + os.linesep + "Select the network and synonym files for DiRaC and Adaptive algorithms."
        class_message = "Label and partition the imported data into classes for training."
        settings_message = "Configure the parameters of the learning algorithms."
        train_message = "Train the learning algorithms according to your settings."
        test_message = "Select a sample from the data and classify it."
        evaluate_message = "Perform cross validation on the models."
        
        dp = self.m.displayPage

        a=self.home_button = Button(self, text="Home", command=lambda:dp('Home'))
        
        b=self.import_button = Button(self, text="Import Data", command=lambda:dp('Import'))
        c=self.class_button = Button(self, text="Class Definition", command=lambda:dp('Class'))
        d=self.settings_button = Button(self, text="Learner Settings", command=lambda:dp('Settings'))
        e=self.train_button = Button(self, text="Train Classifiers", command=lambda:dp('Train'))
        f=self.test_button = Button(self, text="Test Classifiers", command=lambda:dp('Test'))
        g=self.evaluate_button = Button(self, text="Evaluate Performance", command=lambda:dp('Evaluate'))
        
        bm = self.bindMessage
        bm(a,home_message)
        bm(b,import_message)
        bm(c,class_message)
        bm(d,settings_message)
        bm(e,train_message)
        bm(f,test_message)
        bm(g,evaluate_message)
        self.buttonList = [a,b,c,d,e,f,g]
        welcome_img = os.path.join(self.m.controller.workspace, 'data', 'AUREA-logo-200.pgm')
        self.photo = photo = PhotoImage(file=welcome_img)
        self.plabel = Label(self,  image=photo)

    def bindMessage(self, widget, msg):
        import random
        i = random.randint(0,100)
        widget.bind("<Enter>", lambda e: self.messageOn(msg,i))
        widget.bind("<Leave>", lambda e: self.messageOff(i))


    def layoutNav(self):
        """
        Layout Button objects
        """
        for i,button in enumerate(self.buttonList):
            button.grid(row=i, column=0, sticky=E+W,padx=3, pady=4 )
        self.plabel.config(width=200)
        self.plabel.grid(row=len(self.buttonList), column=0)


    def messageOn(self, msg, rand):
        self.tag = rand
        self.plabel = Message(self, text=msg,relief=SUNKEN, width=200 )
        self.plabel.grid(row=len(self.buttonList),column=0, sticky =N+S+E+W)
    
    def messageOff(self,rand):
        from time import sleep
        sleep(.1)
        if self.tag == rand:
            self.plabel = Label(self,  image=self.photo)
            self.plabel.grid(row=len(self.buttonList), column=0, sticky=N+S+E+W)
           
    def nullaction(self):
        print self.m.pack_info()

class AUREAMenu(Menu):
    def __init__(self, daRoot):
        Menu.__init__(self, daRoot)
        self.root = daRoot
        self.buildFile()
        #self.buildSettings()
        self.buildHelp()
        self.dialog = None


    def buildFile(self):
        filemenu = Menu( self )
        self.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Load Settings...", command=self.load_settings)
        filemenu.add_command(label="Save Settings...", command=self.save_settings)

    def buildSettings(self):
        """
        Deprecated, they have their own AUREAPage now.
        """
        raise Exception("menu.buildSettings is deprecated. Use the AUREAPage.learnerSettings")
        settingsmenu = Menu( self )
        self.add_cascade(label="Settings", menu=settingsmenu)
        settingsmenu.add_command(label="Data...", command=self.data_settings)
        settingsmenu.add_command(label="Dirac...", command=self.dirac_settings)
        settingsmenu.add_command(label="TSP...", command=self.tsp_settings)
        settingsmenu.add_command(label="k-TSP...", command=self.ktsp_settings)
        settingsmenu.add_command(label="TST...", command=self.tst_settings)
        settingsmenu.add_command(label="Adaptive...", command=self.adaptive_settings)
         
    def buildHelp(self):
        helpmenu = Menu(self)
        self.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="Content", command=self.unImplemented)
        helpmenu.add_command(label="Report a Problem", command=self.reportProblem)
        helpmenu.add_command(label="About", command=self.about)

    def reportProblem(self):
        msg = "Please go to https://github.com/JohnCEarls/AUREAPackage/issues to report any bugs. Thank you for helping make AUREA better."
        tkMessageBox.showinfo("AUREA: report error", msg)
    
    def about(self):
        msg = "AUREA v. " + AUREA.__version__
        msg += " Copyright (c) 2010-2011 John C. Earls"
        tkMessageBox.showinfo("AUREA", msg)
        

    def dirac_settings(self):
        if self.dialog is None:
            self.settings_display("dirac", self.dirac_settings_write)

    def data_settings(self):
        if self.dialog is None:
            self.settings_display("datatable", self.data_settings_write)

    def data_settings_write(self):
        self.settings_write("datatable")
        self.dialog.destroy()
        self.dialog = None

    
    def settings_display(self, learner, write_function):
        dialog = self.dialog = Toplevel(self.root)
        self.dialog.protocol('WM_DELETE_WINDOW', self.close_window)
        self.dialog.title(learner + " settings")
        self.dialog.transient(self.root)
        self.dialog.geometry("+%d+%d" % (self.root.winfo_rootx()+50,
                                  self.root.winfo_rooty()+50))
        settings = self.root.controller.config.getSettings(learner)
        self.entries = []
        for i, setting in enumerate(settings):
            Label(dialog, text=setting[0]).grid(row=i, column=0)
            c_off = 1
            for j,val in enumerate(setting[1]):
                e = Entry(dialog)
                e.insert(0,val)
                self.entries.append(e)
                e.grid(row=i, column=c_off+j)
        b = Button(dialog, text="OK", command=write_function)
        b.grid(row=len(settings), column=0)
       
    def close_window(self):
        self.dialog.destroy()
        self.dialog = None

    def settings_write(self, learner):
        settings = self.root.controller.config.getSettings(learner)
        curr_entry = 0
        for setting in settings:
            config_list = []
            for x in setting[1]:
                vals = self.entries[curr_entry].get()
                config_list.append(vals)
                curr_entry += 1
            self.root.controller.config.setSetting(learner, setting[0], config_list)

        self.dialog.destroy()
    def dirac_settings_write(self):
        self.settings_write("dirac")
        self.dialog.destroy()
        self.dialog = None

    def tsp_settings(self):
        if self.dialog is None:
            self.settings_display("tsp", self.tsp_settings_write)
    def tsp_settings_write(self):
        self.settings_write("tsp")
        self.dialog.destroy()
        self.dialog = None

    def ktsp_settings(self):
        if self.dialog is None:
            self.settings_display("ktsp", self.ktsp_settings_write)
    def ktsp_settings_write(self):
        self.settings_write("ktsp")
        self.dialog.destroy()
        self.dialog = None

    def tst_settings(self):
        if self.dialog is None:
            self.settings_display("tst", self.tst_settings_write)

    def tst_settings_write(self):
        self.settings_write("tst")
        self.dialog.destroy()
        self.dialog = None

    def adaptive_settings(self):
        if self.dialog is None:
            self.settings_display("adaptive", self.adaptive_settings_write)

    def adaptive_settings_write(self):
        self.settings_write("adaptive")
        self.dialog.destroy()
        self.dialog = None


    def save_settings(self):        
        options = {}
        options['defaultextension'] = '' # couldn't figure out how this works
        if platform.platform()[0:3] != 'Dar':#mac does not like this
            options['filetypes'] = [('xml config', '.xml')]
        options['initialdir'] = 'data'
        options['initialfile'] = ''
        options['parent'] = self
        options['title'] = 'Save config'
        filename = tkFileDialog.asksaveasfilename(**options)
        if filename:
            self.root.controller.config.writeSettings(filename)

    def load_settings(self):
        options = {}
        options['defaultextension'] = '' # couldn't figure out how this works
        if platform.platform()[0:3] != 'Dar':#mac does not like this
            options['filetypes'] = [('xml config', '.xml')]
        options['initialdir'] = 'data'
        options['initialfile'] = 'config.xml'
        options['parent'] = self
        options['title'] = 'Load config'
        filename = tkFileDialog.askopenfilename(**options)
        if filename:
            self.root.controller.config = SettingsParser(filename)


    def unImplemented(self):
        print "unimplemented"
