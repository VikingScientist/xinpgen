from tkinter import font
from tkinter import messagebox
import tkinter as tk
import tkinter.ttk as ttk
import xml.etree.ElementTree as et
from xml.dom import minidom
import glob, os



class Application(tk.Frame):
	def __init__(self, master=None):
		tk.Frame.__init__(self, master)
		### uncomment this to make it resizeable
		# self.grid(sticky=tk.N+tk.S+tk.W+tk.E)
		self.grid()
		self.createWidgets()

	def createWidgets(self):
		self.frames = []
		self.notebook = ttk.Notebook(self)
		self.notebook.grid(sticky=tk.N+tk.S+tk.W+tk.E)
		# for all available xml-files
		for onefile in glob.glob('*.xml'):
			# parse xml-file and generate GUI accordingly
			tree = et.parse(onefile)
			root = tree.getroot()
			for child in root:
				# one frame (tab) for every child of the root node
				self.parseFrame(child)

		### resizing commands
		# top = self.winfo_toplevel()
		# top.rowconfigure(0,weight=1)
		# top.columnconfigure(0,weight=1)

		# self.rowconfigure(0,weight=1)
		# self.columnconfigure(0,weight=1)

		# self.frames[0].rowconfigure(0,weight=1)
		# self.frames[0].columnconfigure(0,weight=1)

		for f in self.frames:
			self.notebook.add(f, text=f.name)

		self.overview = tk.Frame(self)
		self.overview.checkbox = []
		for f in self.frames:
			isOn = tk.IntVar()
			checkbox = tk.Checkbutton(self.overview, state=tk.NORMAL, text=f.name, variable=isOn, onvalue=1, offvalue=0, font=font.Font())
			checkbox.isOn = isOn
			checkbox.invoke()
			checkbox.config(command = lambda checkbox=checkbox: self.activateFrame(checkbox))
			if f.inactive:
				checkbox.invoke()
			# silly lambda functions require the "checkbox=checkbox" hack when used inside for-loops
			checkbox.grid(column=0, sticky=tk.W)

		# let Overview be at the start, and with focus
		self.notebook.insert(0, self.overview, text="Overview")
		self.notebook.select(0)


		# add the button panel at the bottom
		separator = ttk.Separator(self)
		separator.grid(  row=1, sticky=tk.E+tk.W)

		buttonFrame = tk.Frame(self)
		buttonFrame.grid(row=2, sticky=tk.E+tk.W)
		self.saveButton = tk.Button(buttonFrame, text='Save', command=self.save)
		self.saveButton.pack(side='left', expand=True)
		self.quitButton = tk.Button(buttonFrame, text='Quit', command=self.quit)
		self.quitButton.pack(side='right', expand=True)


	def activateFrame(self, caller):
		callerState = caller.config()
		c = caller.cget('variable')
		for t in self.notebook.tabs():
			tabState = self.notebook.tab(t)
			if tabState['text'] == callerState['text'][-1]:
				if caller.isOn.get() == 1:
					self.notebook.tab(t, state=tk.NORMAL)
				else:
					self.notebook.tab(t, state=tk.DISABLED)


	def parseFrame(self, root):
		self.italic = font.Font(slant='italic')
		self.bold   = font.Font(weight='bold')
		thisFrame = tk.Frame(self)
		thisFrame.name   = root.tag
		thisFrame.inactive = ('default' in root.attrib and (root.attrib['default'] == 'False' or root.attrib['default'] == '0'))
		self.frames.append(thisFrame)
		self.rowcount = 0
		self.parseTag(root, thisFrame)

	def isInteger(self, action, index, text):
		try:
			int(text)
			return True
		except ValueError:
			return False

	def isFloat(self, action, index, text):
		try:
			float(text)
			return True
		except ValueError:
			return False
	
	def helpPopup(self, title, message):
		messagebox.showinfo(title, message)

	def parseTag(self, root, frame, prefix=""):
		for child in root.findall("./*[@type='attribute']"):
			label     = ttk.Label(frame, text=prefix + child.tag, font=self.italic)
			label.isChild = False
			if child.attrib['value'] == 'enum':
				choices = [e.text for e in child.findall("./enum")]
				textField = ttk.Combobox(frame, values=choices)
				textField.set(choices[0])
				textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
				if 'default' in child.attrib:
					textField.set(child.attrib['default'])
			elif child.attrib['value'] == 'int':
				okayCommand = frame.register(self.isInteger)
				textField = tk.Entry( frame, validate='all', validatecommand=(okayCommand, '%d', '%i', '%S'))
				textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
				if 'default' in child.attrib:
					textField.set(child.attrib['default'])
			elif child.attrib['value'] == 'float':
				okayCommand = frame.register(self.isFloat)
				textField = tk.Entry( frame, validate='all', validatecommand=(okayCommand, '%d', '%i', '%S'))
				textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
				if 'default' in child.attrib:
					textField.insert(0,child.attrib['default'])
			elif child.attrib['value'] == 'bool':
				isOn = tk.IntVar()
				checkbox = tk.Checkbutton(frame, variable=isOn)
				checkbox.isOn = isOn
				checkbox.grid(row=self.rowcount, column=1, sticky=tk.W)
				if 'default' in child.attrib and child.attrib['default'] == 'True':
					checkbox.invoke()
			else:
				textField = tk.Entry( frame)
				textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
				if 'default' in child.attrib:
					textField.insert(0,child.attrib['default'])


			if 'help' in child.attrib:
				helpButton = tk.Button(frame, text='help', command=lambda title=child.tag, msg=child.attrib['help']: self.helpPopup(title, msg))
				helpButton.grid(row=self.rowcount, column=2)
			else:
				ttk.Label(frame, text='').grid(row=self.rowcount, column=2)

			label.grid(    row=self.rowcount, column=0, sticky=tk.W)
			self.rowcount = self.rowcount + 1
		for child in root.findall("./*[@type='child']"):
			label     = ttk.Label(frame, text=prefix + child.tag, font=self.bold)
			label.grid(row=self.rowcount, column=0, sticky=tk.W)
			label.isChild = True

			if 'value' in child.attrib:
				if child.attrib['value'] == 'enum':
					choices = [e.text for e in child.findall("./enum")]
					textField = ttk.Combobox(frame, values=choices)
					textField.set(choices[0])
					textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
					if 'default' in child.attrib:
						textField.set(child.attrib['default'])
				elif child.attrib['value'] == 'int':
					okayCommand = frame.register(self.isInteger)
					textField = tk.Entry( frame, validate='all', validatecommand=(okayCommand, '%d', '%i', '%S'))
					textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
					if 'default' in child.attrib:
						textField.insert(0,child.attrib['default'])
				elif child.attrib['value'] == 'float':
					okayCommand = frame.register(self.isFloat)
					textField = tk.Entry( frame, validate='all', validatecommand=(okayCommand, '%d', '%i', '%S'))
					textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
					if 'default' in child.attrib:
						textField.insert(0,child.attrib['default'])
				elif child.attrib['value'] == 'bool':
					isOn = tk.IntVar()
					checkbox = tk.Checkbutton(frame, variable=isOn)
					checkbox.isOn = isOn
					checkbox.grid(row=self.rowcount, column=1, sticky=tk.W)
					if 'default' in child.attrib and child.attrib['default'] == 'True':
						checkbox.invoke()
				else:
					textField = tk.Entry( frame)
					textField.grid(row=self.rowcount, column=1, sticky=tk.W+tk.E)
					if 'default' in child.attrib:
						textField.insert(0,child.attrib['default'])
			else:
				ttk.Label(frame, text='').grid(row=self.rowcount, column=1)

			if 'help' in child.attrib:
				helpButton = tk.Button(frame, text='help', command=lambda title=child.tag, msg=child.attrib['help']: self.helpPopup(title, msg))
				helpButton.grid(row=self.rowcount, column=2)
			else:
				ttk.Label(frame, text='').grid(row=self.rowcount, column=2)

			self.rowcount = self.rowcount + 1
			self.parseTag(child, frame, prefix + "  ")

	def save(self):
		root = et.Element('simulation')
		for t in self.notebook.tabs():
			tabState = self.notebook.tab(t)
			if tabState['state'] == 'normal': 
				for f in self.frames:
					if f.name == tabState['text']:
						elm = et.SubElement(root, tabState['text'])
						self.storeTag(elm, f.winfo_children())

		rough_string = et.tostring(root, 'utf-8') # entire xml-file on a single line
		reparsed = minidom.parseString(rough_string)
		result = reparsed.toprettyxml(indent="  ")
		f = open('test.xinp', 'w')
		f.write(result)

	
	# The tree depth level is defined as the number of starting double-spaces in the string
	def getLevel(self, text):
		i = 0
		while(text[i] == ' '):
			i = i+2
		return int(i/2)

	# parses an entire tk.Frame into a xml element node. Alternating Label and
	# text-input gives rise to tag/attribute names and values
	def storeTag(self, element, widgets):
		activeElements = [element]
		lastActive     = 0
		for i in range(int(len(widgets)/3)):
			label  = widgets[3*i]   # this is a ttk.Label
			value  = widgets[3*i+1] # typically tk.Entry or ttk.Combobox
			button = widgets[3*i+2] # this is the help-button, disregard completely

			# extract tag/attribute name and xml level it lives on
			tagname = label.cget('text').strip()
			level   = self.getLevel(label.cget('text'))

			# checkboxes will disable entire tree below it, just keep going
			if level > lastActive:
				continue

			if label.isChild:
				if (type(value) is not tk.Checkbutton) or (
				    type(value) is tk.Checkbutton and value.isOn):
					child = et.SubElement(activeElements[level], tagname)
					if level+1 >= len(activeElements):
						activeElements.append(child)
					else:
						activeElements[level+1] = child
					lastActive = level+1
					try:
						child.text = value.get()
					except AttributeError:
						pass # do nothing
			else: # attribute to existing tag
				if len(value.get()) > 0:
					activeElements[level].attrib[tagname] = value.get()

                

app = Application()
app.master.title('Sample Application')
app.mainloop()
