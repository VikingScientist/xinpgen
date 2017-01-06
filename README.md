# XinpGen

GUI for generating [IFEM](https://github.com/opm/ifem) input files (.xinp) written using the python [tkinter](https://wiki.python.org/moin/TkInter) inteface. It is designed to be minimalistic both from a user- and developer point of view. It will generate an .xinp file from scratch for you and allow you to store this on your computer, nothing more, nothing less.

#### What does it do?

Let's you create an .xinp file by clicking around in a GUI instead of writing it by hand.

#### Why does it do it?

Because remembering every xml-tag and attribute name is hard

#### What does it not do?

Quite a number of things. It does not help you create sensible input (only *legal* input) and it does not have a "load" function to modify existing .xinp files.

#### How does it do it?

Every possible tag and attribute is stored in an xml-file (see `base.xml`) along with its legal input: enum,int,string,bool or float. These xml-files are parsed and dynamically generates the GUI experience. This allows for easy maintnence and extension of the toolbox itself.
