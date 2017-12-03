'''
This is a filter originally made by Texelelf and can be found here
with lots of his other filters : http://elemanser.com/filters.html

This version (modified by gentlegiantJGC) has a few small modifications
that fix errors when using this filter with a bedrock format world.
As such this filter can now be used in both java and bedrock worlds.
'''

import sys
import os
import win32gui, win32api, win32con, winerror, commctrl
import struct, array
import re
from copy import deepcopy
from pymclevel import nbt, TAG_Compound, TAG_List, TAG_Int_Array, TAG_Byte_Array, TAG_String, TAG_Long, TAG_Int, TAG_Short, TAG_Byte, TAG_Double, TAG_Float
import numpy
import mcplatform
import ctypes
from cStringIO import StringIO
import gzip, zlib

displayName = "NBT Editor"

inputs = (
	("Edit...",("Selection","File","level.dat")),
	)

template = {"name":"", "value":None , "id":-1, "type":-1, "hitem":None, "parent":None, "children":[]}

tags = {}
newtag = []
clipboard = []
FindHandle = None
TreeHandle = None

clipidctr = 0
idcounter = 0
targettag = 0

wcscpy = ctypes.cdll.msvcrt.wcscpy
GlobalAlloc = ctypes.windll.kernel32.GlobalAlloc
GlobalLock = ctypes.windll.kernel32.GlobalLock
GlobalUnlock = ctypes.windll.kernel32.GlobalUnlock
OpenClipboard = ctypes.windll.user32.OpenClipboard
EmptyClipboard = ctypes.windll.user32.EmptyClipboard
SetClipboardData = ctypes.windll.user32.SetClipboardData
CloseClipboard = ctypes.windll.user32.CloseClipboard

CreateWindowExW = ctypes.windll.user32.CreateWindowExW
def CreateWindowEx(exstyle, classname, windowname, style, x, y, width, height, parent, menu, instance, lparam):
	return CreateWindowExW(exstyle, ctypes.c_wchar_p(classname), ctypes.c_wchar_p(windowname), style, x, y, width, height, parent, menu, instance, lparam)

GetWindowTextZ = ctypes.windll.user32.GetWindowTextW
GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW

def GetText(hwnd):
	length = GetWindowTextLength(hwnd)
	buff = ctypes.create_unicode_buffer(length + 1)
	GetWindowTextZ(hwnd, buff, length + 1)
	return unicode.replace(buff.value,u"\r\n",u"\n").encode("unicode-escape")
	
SetWindowTextZ = ctypes.windll.user32.SetWindowTextW
def SetText(hwnd,str):
	str = unicode.replace(str,"\0","")
	str = unicode.replace(str,"\n","\r\n")
	str = str + "\0" #C-strings are null-terminated
	buff = ctypes.create_unicode_buffer(str,len(str))
	SetWindowTextZ(hwnd, buff)
	return buff.value

def GetID():
	global idcounter
	idcounter+= 1
	return idcounter

COMPOUND = 0
LIST = 1
LONG = 2
INT = 3
SHORT = 4
BYTE = 5
DOUBLE = 6
FLOAT = 7
INT_ARRAY = 8
BYTE_ARRAY = 9
STRING = 10
UBYTE = 99

iconnames = (	"compound.ico","list.ico","long.ico","integer.ico","short.ico","byte.ico","double.ico","float.ico","int_array.ico","byte_array.ico","string.ico")

tagtypes =	{	TAG_Compound:0, TAG_List:1, TAG_Long:2, TAG_Int:3, TAG_Short:4,TAG_Byte:5, TAG_Double:6, TAG_Float:7,TAG_Int_Array:8, TAG_Byte_Array:9, TAG_String:10 }

IDC_LISTBOX = 1023
IDC_BUTTON_NEW = 1024
IDC_BUTTON_COPY = 1025
IDC_BUTTON_CUT = 1026
IDC_BUTTON_PASTE = 1027
IDC_BUTTON_DELETE = 1028
IDC_BUTTON_DONE = 1029
IDC_BUTTON_EDIT = 1030
IDC_BUTTON_CANCEL = 1031
IDC_BUTTON_VIEW = 1032
IDC_BUTTON_PLUS = 1033
IDC_BUTTON_MINUS = 1034
IDC_BUTTON_FIND = 1035
IDC_BUTTON_EXPAND = 1036

CDC_BUTTON_DONE = 1125
CDC_BYTERADIO = 1127
CDC_SELECTALL = 1128
CDC_INSERTTAB = 1129
CDC_FORMATTEXT = 1130
CDC_BYTECHECK = 1131
CDC_SECTION = 1132
CDC_HEX = 1133

CDC_EXACT_NAME = 1134
CDC_EXACT_VALUE = 1135
CDC_MATCH_CASE = 1136

is64bit = "64 bit" in sys.version

if win32gui.UNICODE:
	def _make_text_buffer(text):
		# XXX - at this stage win32gui.UNICODE is only True in py3k,
		# and in py3k is makes sense to reject bytes.
		if not isinstance(text, unicode):
			raise TypeError('MENUITEMINFO text must be unicode')
		data = (text+'\0').encode("unicode-internal")
		return array.array("b", data)

else:
	def _make_text_buffer(text):
		if isinstance(text, unicode):
			text = text.encode("mbcs")
		return array.array("b", text+'\0')

# make an 'empty' buffer, ready for filling with cch characters.
def _make_empty_text_buffer(cch):
	return _make_text_buffer("\0" * cch)

if sys.version_info < (3,0):
	def _make_memory(ob):
		return str(buffer(ob))

	def _make_bytes(sval):
		return sval
else:
	def _make_memory(ob):
		return bytes(memoryview(ob))

	def _make_bytes(sval):
		return sval.encode('ascii')

try:
	from collections import namedtuple
	def _MakeResult(names_str, values):
		names = names_str.split()
		nt = namedtuple(names[0], names[1:])
		return nt(*values)
except ImportError:
	# no namedtuple support - just return the values as a normal tuple.
	def _MakeResult(names_str, values):
		return values

def _GetMaskAndVal(val, default, mask, flag):
	if val is None:
		return mask, default
	else:
		if flag is not None:
			mask |= flag
		return mask, val

_nmhdr_fmt = "PPi"
if is64bit:

	_nmhdr_align_padding = "xxxx"
else:
	_nmhdr_align_padding = ""

_tvitem_fmt = "iPiiPiiiiP"

def PackTVINSERTSTRUCT(parent, insertAfter, tvitem):
	tvitem_buf, extra = PackTVITEM(*tvitem)
	tvitem_buf = tvitem_buf.tostring()
	format = "PP%ds" % len(tvitem_buf)
	return struct.pack(format, parent, insertAfter, tvitem_buf), extra

def PackTVITEM(hitem, state, stateMask, text, image, selimage, citems, param):
	extra = []
	mask = 0
	mask, hitem = _GetMaskAndVal(hitem, 0, mask, commctrl.TVIF_HANDLE)
	mask, state = _GetMaskAndVal(state, 0, mask, commctrl.TVIF_STATE)
	if not mask & commctrl.TVIF_STATE:
		stateMask = 0
	mask, text = _GetMaskAndVal(text, None, mask, commctrl.TVIF_TEXT)
	mask, image = _GetMaskAndVal(image, 0, mask, commctrl.TVIF_IMAGE)
	mask, selimage = _GetMaskAndVal(selimage, 0, mask, commctrl.TVIF_SELECTEDIMAGE)
	mask, citems = _GetMaskAndVal(citems, 0, mask, commctrl.TVIF_CHILDREN)
	mask, param = _GetMaskAndVal(param, 0, mask, commctrl.TVIF_PARAM)
	if text is None:
		text_addr = text_len = 0
	else:
		text_buffer = _make_text_buffer(text)
		text_len = len(text)
		extra.append(text_buffer)
		text_addr, _ = text_buffer.buffer_info()
	buf = struct.pack(_tvitem_fmt, mask, hitem, state, stateMask, text_addr, text_len, image, selimage, citems, param)
	return array.array("b", buf), extra

def EmptyTVITEM(hitem, mask = None, text_buf_size=512):
	extra = []
	if mask is None:
		mask = commctrl.TVIF_HANDLE | commctrl.TVIF_STATE | commctrl.TVIF_TEXT | \
			   commctrl.TVIF_IMAGE | commctrl.TVIF_SELECTEDIMAGE | \
			   commctrl.TVIF_CHILDREN | commctrl.TVIF_PARAM
	if mask & commctrl.TVIF_TEXT:
		text_buffer = _make_empty_text_buffer(text_buf_size)
		extra.append(text_buffer)
		text_addr, _ = text_buffer.buffer_info()
	else:
		text_addr = text_buf_size = 0
	buf = struct.pack(_tvitem_fmt, mask, hitem, 0, 0, text_addr, text_buf_size, 0, 0, 0, 0)
	return array.array("b", buf), extra
	
def UnpackTVITEM(buffer):
	item_mask, item_hItem, item_state, item_stateMask, item_textptr, item_cchText, item_image, item_selimage, item_cChildren, item_param = struct.unpack(_tvitem_fmt, buffer)
	if not (item_mask & commctrl.TVIF_TEXT): item_textptr = item_cchText = None
	if not (item_mask & commctrl.TVIF_CHILDREN): item_cChildren = None
	if not (item_mask & commctrl.TVIF_IMAGE): item_image = None
	if not (item_mask & commctrl.TVIF_PARAM): item_param = None
	if not (item_mask & commctrl.TVIF_SELECTEDIMAGE): item_selimage = None
	if not (item_mask & commctrl.TVIF_STATE): item_state = item_stateMask = None
	
	text = None

#TexelElf:
#The following lines spam ValueError exceptions when used in unpacking WM_NOTIFY messages.  According to
#MSDN at http://msdn.microsoft.com/en-us/library/windows/desktop/bb773544%28v=vs.85%29.aspx 
#    "Only the mask, hItem, state, and lParam members of these (TVITEM) structures are valid."
#As I have no need to extract the item text, I'm not fixing it by creating a separate UnpackTVITEM for WM_NOTIFY

#	if item_textptr:
#		text = win32gui.PyGetString(item_textptr)
#	else:
#		text = None


	return _MakeResult("TVITEM item_hItem item_state item_stateMask "
					   "text item_image item_selimage item_cChildren item_param",
					   (item_hItem, item_state, item_stateMask, text,
						item_image, item_selimage, item_cChildren, item_param))

# Unpack the lparm from a "TVNOTIFY" message
def UnpackTVNOTIFY(lparam):
	item_size = struct.calcsize(_tvitem_fmt)
	format = _nmhdr_fmt + _nmhdr_align_padding
	if is64bit:
		format = format + "ixxxx"
	else:
		format = format + "i"
	format = format + "%ds%ds" % (item_size, item_size)
	buf = win32gui.PyGetMemory(lparam, struct.calcsize(format))
	hwndFrom, id, code, action, buf_old, buf_new = struct.unpack(format, buf)
	item_old = UnpackTVITEM(buf_old)
	item_new = UnpackTVITEM(buf_new)
	return _MakeResult("TVNOTIFY hwndFrom id code action item_old item_new",
					   (hwndFrom, id, code, action, item_old, item_new))

def UnpackTVDISPINFO(lparam):
	item_size = struct.calcsize(_tvitem_fmt)
	format = "PPi%ds" % (item_size,)
	buf = win32gui.PyGetMemory(lparam, struct.calcsize(format))
	hwndFrom, id, code, buf_item = struct.unpack(format, buf)
	item = UnpackTVITEM(buf_item)
	return _MakeResult("TVDISPINFO hwndFrom id code item",
						(hwndFrom, id, code, item))

def NBT2Command(nbtData):
	command = ""
	if type(nbtData) is TAG_List:
		list = True
	else:
		list = False

	if type(nbtData) in (TAG_Compound, TAG_List):
		for tag in range(0,len(nbtData)) if list else nbtData.keys():
			if type(nbtData[tag]) is TAG_Compound:
				if not list:
					if tag != "":
						command += tag+":"
				command += "{"
				command += NBT2Command(nbtData[tag])
				command += "}"
			elif type(nbtData[tag]) is TAG_List:
				if not list:
					if tag != "":
						command += tag+":"
				command += "["
				command += NBT2Command(nbtData[tag])
				command += "]"
			else:
				if not list:
					if tag != "":
						command += tag+":"
				if type(nbtData[tag]) is TAG_String:
					command += "\""
					command += str.replace(nbtData[tag].value.encode("unicode-escape"), r'"',r'\\"')
					command += "\""
				else:
					if type(nbtData[tag]) == TAG_Byte_Array:
						command += "["+",".join(["%sb" % num for num in nbtData[tag].value.astype("str")])+"]"
					elif type(nbtData[tag]) == TAG_Int_Array:
						command += "["+",".join(nbtData[tag].value.astype("str"))+"]"
					else:
						command += nbtData[tag].value.encode("unicode-escape") if isinstance(nbtData[tag].value, unicode) else str(nbtData[tag].value)
						if type(nbtData[tag]) is TAG_Byte:
							command += "b"
						elif type(nbtData[tag]) is TAG_Short:
							command += "s"
						elif type(nbtData[tag]) is TAG_Long:
							command += "l"
						elif type(nbtData[tag]) is TAG_Float:
							command += "f"
						elif type(nbtData[tag]) is TAG_Double:
							command += "d"			
				
			command += ","
		else:
			if command != "":
				if command[-1] == ",":
					command = command[:-1]
	else:
		if nbtData.name != "":
			command += nbtData.name+":"
		if type(nbtData) is TAG_String:
			command += "\""
			command += str.replace(nbtData.value.encode("unicode-escape"), r'"',r'\\"')
			command += "\""
		else:
			if type(nbtData) == TAG_Byte_Array:
				command += "["+",".join(["%sb" % num for num in nbtData.value.astype("str")])+"]"
			elif type(nbtData) == TAG_Int_Array:
				command += "["+",".join(nbtData.value.astype("str"))+"]"
			else:
				command += nbtData.value.encode("unicode-escape") if isinstance(nbtData.value, unicode) else str(nbtData.value)
				if type(nbtData) is TAG_Byte:
					command += "b"
				elif type(nbtData) is TAG_Short:
					command += "s"
				elif type(nbtData) is TAG_Long:
					command += "l"
				elif type(nbtData) is TAG_Float:
					command += "f"
				elif type(nbtData) is TAG_Double:
					command += "d"			

	return command

def indent(ct):
	return "    "*ct

def strexplode(command):
	coms = []
	if not command:
		return coms
	i = 0
	line = ""
	inquote = 0
	for c in xrange(len(command)):
		if command[c] == "{":
			if inquote:
				line += command[c]
			else:
				if line:
					coms.append(indent(i)+line)
					line = ""
				coms.append(indent(i)+"{")
				i += 1
		elif command[c] == "}":
			if inquote:
				line += command[c]
			else:
				if line:
					coms.append(indent(i)+line)
					line = ""
				i -= 1
				line += command[c]
		elif command[c] == "[":
			if inquote:
				line += command[c]
			else:
				if line:
					coms.append(indent(i)+line)
					line = ""
				coms.append(indent(i)+"[")
				i += 1
		elif command[c] == "]":
			if inquote:
				line += command[c]
			else:
				if line:
					coms.append(indent(i)+line)
					line = ""
				i -= 1
				line += command[c]
		elif command[c] == '\"':
			if command[c-1] != "\\":
				inquote ^= 1
			line += command[c]
		elif command[c] == ",":
			if inquote:
				line += command[c]
			else:
				coms.append(indent(i)+line+",")
				line = ""
		else:
			line += command[c]
	else:
		if line:
			coms.append(indent(i)+line)
	return coms

def strcollapse(lines):
	command = ""
	if len(lines) < 1:
		return command
	elif len(lines) == 1:
		return lines[0]

	if lines[0] == "{":
		command += lines[0].lstrip().rstrip()
	else:
		command += lines[0].lstrip().rstrip() + " "
	for l in lines:
		if not l:
			continue
		if lines.index(l) == 0:
			continue
		command += l.lstrip().rstrip()
	return command
						
class DialogBase(object):
	def __init__(self):
		win32gui.InitCommonControls()
		self.hinst = win32gui.dllhandle
		self.current_hitem = None
		self.current_lparam = None
		self.title = "NBT Editor"
		self.modified = False


	def _RegisterWndClass(self):
		className = "NBTEditorWindowClass"
		message_map = {}
		wc = win32gui.WNDCLASS()
		wc.SetDialogProc()
		wc.hInstance = self.hinst
		wc.lpszClassName = className
		wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
		wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
		wc.hbrBackground = win32con.COLOR_WINDOW + 1
		wc.lpfnWndProc = message_map
		# C code: wc.cbWndExtra = DLGWINDOWEXTRA + sizeof(HBRUSH) + (sizeof(COLORREF));
		wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
		icon_flags = win32con.LR_DEFAULTSIZE
		wc.hIcon=0

		try:
			classAtom = win32gui.RegisterClass(wc)
		except win32gui.error, err_info:
			if err_info.winerror!=winerror.ERROR_CLASS_ALREADY_EXISTS:
				raise
		return className

	def _GetDialogTemplate(self, dlgClassName):
		style = win32con.WS_BORDER | win32con.WS_VISIBLE | win32con.WS_CAPTION | win32con.WS_SYSMENU
		cs = win32con.WS_CHILD | win32con.WS_VISIBLE

		dlg = [ [self.title, (0, 0, 440, 412), style, None, (8, "MS Sans Serif"), None, dlgClassName], ]
		dlg.append([128, "&New", IDC_BUTTON_NEW, (0, 398, 30, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "&Edit", IDC_BUTTON_EDIT, (30, 398, 30, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "&Delete", IDC_BUTTON_DELETE, (60, 398, 30, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "&Copy", IDC_BUTTON_COPY, (90, 398, 30, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "C&ut", IDC_BUTTON_CUT, (120, 398, 30, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "&Paste", IDC_BUTTON_PASTE, (150, 398, 30, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "Clipboard", IDC_BUTTON_VIEW, (180, 398, 35, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "Expand", IDC_BUTTON_EXPAND, (243, 398, 40, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "&Find", IDC_BUTTON_FIND, (283, 398, 36, 14), cs | win32con.BS_PUSHBUTTON])
		dlg.append([128, "D&one", IDC_BUTTON_DONE, (320, 398, 60, 14), cs | win32con.BS_DEFPUSHBUTTON])
		dlg.append([128, "C&ancel", win32con.IDCANCEL, (380, 398, 60, 14), cs | win32con.BS_PUSHBUTTON])
		
		return dlg

	def _DoCreate(self, fn, hwnd):
		message_map = {
			win32con.WM_COMMAND: self.OnCommand,
			win32con.WM_NOTIFY: self.OnNotify,
			win32con.WM_INITDIALOG: self.OnInitDialog,
			win32con.WM_CLOSE: self.OnClose,
			win32con.WM_DESTROY: self.OnDestroy,
		}
		dlgClassName = self._RegisterWndClass()
		template = self._GetDialogTemplate(dlgClassName)
		return fn(self.hinst, template, hwnd, message_map)

	def _SetupList(self):
		global tags, TreeHandle
		self.hfont = win32gui.SendMessage(self.hwnd, win32con.WM_GETFONT, 0, 0)
		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.WS_HSCROLL | win32con.WS_VSCROLL
		child_style |= commctrl.TVS_HASLINES | commctrl.TVS_HASBUTTONS | commctrl.TVS_LINESATROOT | commctrl.TVS_SHOWSELALWAYS
		TreeHandle = self.hwndTree = CreateWindowEx(0,"SysTreeView32", None, child_style, 0, 0, 660, 646, self.hwnd, IDC_LISTBOX, self.hinst, None)

		blarg,asdff = PackTVINSERTSTRUCT(0,commctrl.TVI_ROOT,(None,None,None,tags[0]["name"],tags[0]["type"],tags[0]["type"],None,0))
		self.htreeRoot = win32gui.SendMessage(self.hwndTree, commctrl.TVM_INSERTITEM, 0, blarg)
		tags[0]["hitem"] = self.htreeRoot

		pathdir = os.path.join(mcplatform.filtersDir,"NBT_icons")
		if os.path.isdir(pathdir):
			il = win32gui.ImageList_Create(12,16,commctrl.ILC_COLOR32 | commctrl.ILC_MASK,11,0)
			for i in iconnames:
				large, small = win32gui.ExtractIconEx(os.path.join(pathdir,i), 0, 1)
				win32gui.ImageList_ReplaceIcon(il, -1, large[0])
				win32gui.DestroyIcon(small[0])
				win32gui.DestroyIcon(large[0])
			win32gui.SendMessage(self.hwndTree, commctrl.TVM_SETIMAGELIST, commctrl.TVSIL_NORMAL, il)

		for i in tags[0]["children"]:
			self.FillTree(i,self.htreeRoot)
		win32gui.SendMessage(self.hwndTree, commctrl.TVM_EXPAND, commctrl.TVE_EXPAND, self.htreeRoot)

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON
		self.PlusButton = CreateWindowEx(0,"BUTTON", u"\u2191", child_style, 323, 647, 21, 23, self.hwnd, IDC_BUTTON_PLUS, self.hinst, None)
		win32gui.SendMessage(self.PlusButton, win32con.WM_SETFONT, self.hfont, 0)
		
		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON
		self.MinusButton = CreateWindowEx(0,"BUTTON", u"\u2193", child_style, 344, 647, 21, 23, self.hwnd, IDC_BUTTON_MINUS, self.hinst, None)
		win32gui.SendMessage(self.MinusButton, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.EnableWindow(self.PlusButton,False)
		win32gui.EnableWindow(self.MinusButton,False)
		
		win32gui.UpdateWindow(self.hwnd)

	def OnInitDialog(self, hwnd, msg, wparam, lparam):
		self.hwnd = hwnd
		self._SetupList()

	def OnNotify(self, hwnd, msg, wparam, lparam):
		global tags, targettag
		info = UnpackTVNOTIFY(lparam)
		if info.code == commctrl.NM_DBLCLK:
			self.EditTag()
#		elif info.code == commctrl.NM_RCLICK:
#				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_NEW, 0)
		elif info.code == commctrl.TVN_KEYDOWN:
			if (win32api.GetKeyState(win32con.VK_CONTROL)>>15)&1 and (win32api.GetKeyState(67)>>15)&1:
				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_COPY, 0)
			elif (win32api.GetKeyState(win32con.VK_CONTROL)>>15)&1 and (win32api.GetKeyState(88)>>15)&1:
				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_CUT, 0)
			elif (win32api.GetKeyState(win32con.VK_CONTROL)>>15)&1 and (win32api.GetKeyState(86)>>15)&1:
				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_PASTE, 0)
			elif (win32api.GetKeyState(win32con.VK_CONTROL)>>15)&1 and (win32api.GetKeyState(78)>>15)&1:
				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_NEW, 0)
			elif (win32api.GetKeyState(win32con.VK_CONTROL)>>15)&1 and (win32api.GetKeyState(69)>>15)&1:
				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_EDIT, 0)
			elif (win32api.GetKeyState(win32con.VK_DELETE)>>15)&1:
				win32gui.SendMessage(self.hwnd, win32con.WM_COMMAND, IDC_BUTTON_DELETE, 0)

		elif info.code == commctrl.TVN_SELCHANGED:
			self.current_hitem = info.item_new.item_hItem
			targettag = self.current_lparam = info.item_new.item_param
			if tags[self.current_lparam]["parent"]:
				if tags[tags[self.current_lparam]["parent"]]["type"] == LIST:
					win32gui.EnableWindow(self.PlusButton,True)
					win32gui.EnableWindow(self.MinusButton,True)
					return 1
			win32gui.EnableWindow(self.PlusButton,False)
			win32gui.EnableWindow(self.MinusButton,False)
		return 1
		
	def OnCommand(self, hwnd, msg, wparam, lparam):
		global targettag, tags, clipboard, newtag
		id = win32api.LOWORD(wparam)
		if id == IDC_BUTTON_DELETE:
			if self.current_lparam != 0 and self.current_lparam != None:
				win32gui.SetFocus(self.hwndTree)
				self.DeleteItem(self.current_lparam)
				win32gui.PostMessage(self.hwndTree, commctrl.TVM_DELETEITEM, 0, self.current_hitem)
				self.modified = True				
		elif id == IDC_BUTTON_NEW:
			win32gui.SetFocus(self.hwndTree)
			targettag = self.current_lparam
			w=NewDialog()
			if w.Create(self.hwnd):
				if newtag:
					insertop = newtag[3]
					tg = deepcopy(template)
					tg["name"] = 0 if newtag[0] == "" else newtag[0]
					tg["type"] = newtag[2]
					tg["value"] = newtag[1]
					if insertop:
						if tags[targettag]["type"] == LIST:
							isList = True
							tg["name"] = 0
							if tg["type"] == COMPOUND:
								tg["value"] = 0
						newID = GetID()
						tags[newID] = tg
						tags[newID]["id"] = newID
						tags[newID]["parent"] = targettag
						self.FillTree(newID,tags[targettag]["hitem"])
						tags[targettag]["children"].append(newID)
					else:
						if tags[tags[targettag]["parent"]]["type"] == LIST:
							isList = True
							tg["name"] = 0
							if tg["type"] == COMPOUND:
								tg["value"] = 0
						newID = GetID()
						tags[newID] = tg
						tags[newID]["id"] = newID
						tags[newID]["parent"] = tags[targettag]["parent"]
						self.FillTree(newID,tags[tags[targettag]["parent"]]["hitem"])
						tags[tags[targettag]["parent"]]["children"].append(newID)				
					self.modified = True
		elif id == IDC_BUTTON_COPY:
			if self.current_lparam != 0 and self.current_lparam != None:
				win32gui.SetFocus(self.hwndTree)
				del clipboard
				clipboard = {}
				self.CopyItem(clipboard, self.current_lparam)
				clipval = ""
				if clipboard[0]["type"] == COMPOUND and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "{"
				elif clipboard[0]["type"] == LIST and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "["
				clipval += NBT2Command(Serialize(clipboard,0, TAG_Compound(), True if clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long)) else False))
				if clipboard[0]["type"] == COMPOUND and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "}"
				elif clipboard[0]["type"] == LIST and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "]"
				clipval += "\0"

				OpenClipboard(0)
				EmptyClipboard()
				hMem = GlobalAlloc(0x2000, len(clipval.decode("unicode-escape").encode("utf-16le"))+1)
				hChunk = GlobalLock(hMem)
				wcscpy(ctypes.c_char_p(hChunk), clipval.decode("unicode-escape").encode("utf-16le"))
				GlobalUnlock(hMem)
				SetClipboardData(13,hMem)
				CloseClipboard()
		elif id == IDC_BUTTON_CUT:
			if self.current_lparam != 0 and self.current_lparam != None:
				win32gui.SetFocus(self.hwndTree)
				del clipboard
				clipboard = {}
				self.CopyItem(clipboard, self.current_lparam)

				self.DeleteItem(self.current_lparam)
				win32gui.PostMessage(self.hwndTree, commctrl.TVM_DELETEITEM, 0, self.current_hitem)
				self.modified = True				

				clipval = ""
				if clipboard[0]["type"] == COMPOUND and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "{"
				elif clipboard[0]["type"] == LIST and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "["
				clipval += NBT2Command(Serialize(clipboard,0, TAG_Compound(), True if clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long)) else False))
				if clipboard[0]["type"] == COMPOUND and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "}"
				elif clipboard[0]["type"] == LIST and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
					clipval += "]"
				clipval += "\0"
				OpenClipboard(0)
				EmptyClipboard()
				hMem = GlobalAlloc(0x2000, len(clipval.decode("unicode-escape").encode("utf-16le"))+1)
				hChunk = GlobalLock(hMem)
				wcscpy(ctypes.c_char_p(hChunk), clipval.decode("unicode-escape").encode("utf-16le"))
				GlobalUnlock(hMem)
				SetClipboardData(13,hMem)
				CloseClipboard()
		elif id == IDC_BUTTON_PASTE:
			if not clipboard:
				return
			win32gui.SetFocus(self.hwndTree)
			targettag = self.current_lparam
			if tags[targettag]["type"] == COMPOUND:
				if clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long)):
					w = PesterDialog()
					if not w.Create(self.hwnd):
						return
					clipboard[0]["name"] = newtag[0]
				else:
					for c in tags[targettag]["children"]:
						if tags[c]["name"] == clipboard[0]["name"]:
							w = PesterDialog()
							if not w.Create(self.hwnd):
								return
							clipboard[0]["name"] = newtag[0]
							break	
			elif tags[targettag]["type"] == LIST:
				if tags[targettag]["children"]:
					if clipboard[0]["type"] != tags[tags[targettag]["children"][0]]["type"]:
						win32gui.MessageBox(self.hwnd, "The copied tag's type does not match the List child tag type.  Lists can only hold one tag type.", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
						return
					clipboard[0]["name"] = 0
				else:
					clipboard[0]["name"] = 0
			else:
				targettag = tags[targettag]["parent"]
				if clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long)):
					w = PesterDialog()
					if not w.Create(self.hwnd):
						return
					clipboard[0]["name"] = newtag[0]
				else:
					for c in tags[targettag]["children"]:
						if tags[c]["name"] == clipboard[0]["name"]:
							w = PesterDialog()
							if not w.Create(self.hwnd):
								return
							clipboard[0]["name"] = newtag[0]
							break
			self.InsertItem(targettag)
			self.FillTree(tags[targettag]["children"][-1],tags[targettag]["hitem"])
			self.modified = True
			targettag = self.current_lparam

		elif id == IDC_BUTTON_EXPAND:
			global idcounter
			for a in range(idcounter+1):
				win32gui.SendMessage(self.hwndTree, commctrl.TVM_EXPAND, commctrl.TVE_EXPAND, tags[a]["hitem"])

		elif id == IDC_BUTTON_VIEW:
			if not clipboard:
				return
			CreateClipboardDialog(self.hwnd)
		elif id == IDC_BUTTON_DONE:
			if FindHandle:
				win32gui.EndDialog(FindHandle, 0)
			win32gui.EndDialog(self.hwnd, 1)
		elif id == win32con.IDCANCEL:
			if self.modified:
				docancel = win32gui.MessageBox(self.hwnd, "Changes have been made.  Discard these changes?", "Warning", win32con.MB_YESNO | win32con.MB_ICONWARNING)
				if docancel == win32con.IDNO:
					return
			if FindHandle:
				win32gui.EndDialog(FindHandle, 0)
			win32gui.EndDialog(self.hwnd, 0)
		elif id == IDC_BUTTON_EDIT:
			win32gui.SetFocus(self.hwndTree)
			self.EditTag()
		elif id == IDC_BUTTON_PLUS:
			win32gui.SetFocus(self.hwndTree)
			parent = tags[self.current_lparam]["parent"]
			if tags[parent]["type"] == LIST:
				ind = tags[parent]["children"].index(self.current_lparam)
				if ind == 0:
					return 1
				val = tags[parent]["children"].pop(ind)
				tags[parent]["children"].insert(ind-1,val)
				if ind-1 == 0:
					insert = commctrl.TVI_FIRST
				else:
					insert = tags[tags[parent]["children"][ind-2]]["hitem"]
				win32gui.PostMessage(self.hwndTree, commctrl.TVM_DELETEITEM, 0, tags[self.current_lparam]["hitem"])
				self.FillTree(self.current_lparam,tags[parent]["hitem"],insert)
				win32gui.SendMessage(self.hwndTree, commctrl.TVM_EXPAND, commctrl.TVE_EXPAND, tags[self.current_lparam]["hitem"])
				win32gui.PostMessage(self.hwndTree, commctrl.TVM_SELECTITEM, commctrl.TVGN_CARET, tags[self.current_lparam]["hitem"])

		elif id == IDC_BUTTON_MINUS:
			win32gui.SetFocus(self.hwndTree)
			parent = tags[self.current_lparam]["parent"]
			if tags[parent]["type"] == LIST:
				ind = tags[parent]["children"].index(self.current_lparam)
				if ind == len(tags[parent]["children"])-1:
					return 1
				val = tags[parent]["children"].pop(ind)
				tags[parent]["children"].insert(ind+1,val)
				if ind+1 == len(tags[parent]["children"])-1:
					insert = commctrl.TVI_LAST
				else:
					insert = tags[tags[parent]["children"][ind]]["hitem"]
				win32gui.PostMessage(self.hwndTree, commctrl.TVM_DELETEITEM, 0, tags[self.current_lparam]["hitem"])
				self.FillTree(self.current_lparam,tags[parent]["hitem"],insert)
				win32gui.SendMessage(self.hwndTree, commctrl.TVM_EXPAND, commctrl.TVE_EXPAND, tags[self.current_lparam]["hitem"])
				win32gui.PostMessage(self.hwndTree, commctrl.TVM_SELECTITEM, commctrl.TVGN_CARET, tags[self.current_lparam]["hitem"])

		elif id == IDC_BUTTON_FIND:
			targettag = self.current_lparam
			if not FindHandle:
				w=FindDialog()
				w.Create(0)
			else:
				win32gui.SetFocus(FindHandle)				
		return 1

			
	def OnClose(self, hwnd, msg, wparam, lparam):
		raise NotImplementedError

	def OnDestroy(self, hwnd, msg, wparam, lparam):
		pass

	def FillTree(self, tag_num, parent, insertat=None):
		global tags
		if type(tag_num) is list:
			for tag in tag_num:
				if tags[tag]["type"] in (COMPOUND, LIST):
					if isinstance(tags[tag]["name"], (int,long)):
						blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_LAST,(None,None,None,None,tags[tag]["type"],tags[tag]["type"],None,tag))
					else:
						blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_SORT,(None,None,None,unicode(unicode(tags[tag]["name"])),tags[tag]["type"],tags[tag]["type"],None,tag))
				else:
					if isinstance(tags[tag]["name"], (int,long)):
						blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_LAST,(None,None,None,unicode(unicode(tags[tag]["value"])),tags[tag]["type"],tags[tag]["type"],None,tag))
					else:
						blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_SORT,(None,None,None,unicode(unicode(tags[tag]["name"])+": "+unicode(tags[tag]["value"])),tags[tag]["type"],tags[tag]["type"],None,tag))
				tags[tag]["hitem"] = win32gui.SendMessage(self.hwndTree, commctrl.TVM_INSERTITEM, 0, blarg)
				if tags[tag]["type"] in (COMPOUND, LIST):
					self.FillTree(tags[tag]["children"],tags[tag]["hitem"])
		else:
			if tags[tag_num]["type"] in (COMPOUND, LIST):
				if isinstance(tags[tag_num]["name"], (int,long)):
					blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_LAST,(None,None,None,None,tags[tag_num]["type"],tags[tag_num]["type"],None,tag_num))
				else:
					blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_SORT,(None,None,None,unicode(unicode(tags[tag_num]["name"])),tags[tag_num]["type"],tags[tag_num]["type"],None,tag_num))
			else:
				if isinstance(tags[tag_num]["name"], (int,long)):
					blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_LAST,(None,None,None,unicode(unicode(tags[tag_num]["value"])),tags[tag_num]["type"],tags[tag_num]["type"],None,tag_num))
				else:
					blarg,asdff = PackTVINSERTSTRUCT(parent,insertat or commctrl.TVI_SORT,(None,None,None,unicode(unicode(tags[tag_num]["name"])+unicode(": ")+unicode(tags[tag_num]["value"])),tags[tag_num]["type"],tags[tag_num]["type"],None,tag_num))
			tags[tag_num]["hitem"] = win32gui.SendMessage(self.hwndTree, commctrl.TVM_INSERTITEM, 0, blarg)
			if tags[tag_num]["type"] in (COMPOUND, LIST):
				self.FillTree(tags[tag_num]["children"],tags[tag_num]["hitem"])
	

	def EditTag(self):
		global tags, targettag, newtag
		if self.current_lparam == 0: #cannot edit the tree's root node
			return
		targettag = self.current_lparam
		if tags[tags[targettag]["parent"]]["type"] == LIST and tags[targettag]["type"] == COMPOUND:
			return
		else:
			w=EditDialog()
			if w.Create(self.hwnd):
				if newtag:
					self.modified = True
					if newtag[0] != "":
						tags[targettag]["name"] = newtag[0]
					if newtag[2] in (COMPOUND, LIST):
						tags[targettag]["value"] = 0
					else:
						tags[targettag]["value"] = newtag[1]
					tags[targettag]["type"] = newtag[2]
					if tags[targettag]["type"] in (COMPOUND, LIST):
						if isinstance(tags[targettag]["name"], (int,long)):
							blarg,asdff = PackTVITEM(tags[targettag]["hitem"],None,None,None,tags[targettag]["type"],tags[targettag]["type"],None,None)
						else:
							blarg,asdff = PackTVITEM(tags[targettag]["hitem"],None,None,unicode(unicode(tags[targettag]["name"])),tags[targettag]["type"],tags[targettag]["type"],None,None)
					else:
						if isinstance(tags[targettag]["value"], (str,unicode)):
							tags[targettag]["value"] = tags[targettag]["value"].encode("unicode-escape").decode("unicode-escape")
						if isinstance(tags[targettag]["name"], (int,long)):
							blarg,asdff = PackTVITEM(tags[targettag]["hitem"],None,None,unicode(unicode(tags[targettag]["value"])),tags[targettag]["type"],tags[targettag]["type"],None,None)
						else:
							blarg,asdff = PackTVITEM(tags[targettag]["hitem"],None,None,unicode(unicode(tags[targettag]["name"])+": "+unicode(tags[targettag]["value"])),tags[targettag]["type"],tags[targettag]["type"],None,None)
					win32gui.SendMessage(self.hwndTree, commctrl.TVM_SETITEM, 0, blarg)

	def DeleteItem(self, lparam):
		global tags
		for c in tags[lparam]["children"]:
			self.DeleteItem(c)
		tags[tags[lparam]["parent"]]["children"].remove(lparam)
		del tags[lparam]

	def CopyItem(self, result, lparam, parent=None, ID=False):
		global tags, clipidctr
		if ID:
			clipidctr += 1
		else:
			clipidctr = 0
		result[clipidctr] = deepcopy(tags[lparam])
		result[clipidctr]["id"] = clipidctr
		result[clipidctr]["parent"] = parent
		if parent != None:
			result[parent]["children"].append(clipidctr)
		result[clipidctr]["children"] = []
		clipidctrnow = clipidctr
		for c in tags[lparam]["children"]:
			self.CopyItem(result,c,clipidctrnow,True)
	
	def InsertItem(self,lparam,clipid=0):
		global tags, clipboard
		newitem = GetID()
		tags[lparam]["children"].append(newitem)
		tags[newitem] = deepcopy(clipboard[clipid])
		tags[newitem]["id"] = newitem
		tags[newitem]["parent"] = lparam
		tags[newitem]["hitem"] = None
		tags[newitem]["children"] = []
		for c in clipboard[clipid]["children"]:
			self.InsertItem(newitem,c)
		
class Dialog(DialogBase):
	def Create(self,hwnd):
		return self._DoCreate(win32gui.DialogBoxIndirect,hwnd)

	def OnClose(self, hwnd, msg, wparam, lparam):
		if self.modified:
			docancel = win32gui.MessageBox(self.hwnd, "Changes have been made.  Discard these changes?", "Warning", win32con.MB_YESNO | win32con.MB_ICONWARNING)
			if docancel == win32con.IDNO:
				return
		win32gui.EndDialog(hwnd, 0)

def CreateDialog(hwnd):
	w=Dialog()
	return w.Create(hwnd)

def CreateClipboardDialog(hwnd):
	w=NBTString()
	return w.Create(hwnd)

class NBTString(Dialog):
	def __init__(self):
		super(NBTString,self).__init__()
		self.title = "Clipboard Viewer (Read-Only)"

	def OnCommand(self, hwnd, msg, wparam, lparam):
		return 1

	def _SetupList(self):
		global tags, targettag, clipboard
		self.groupBox = self.hwnd
		self.hfont = win32gui.SendMessage(self.hwnd, win32con.WM_GETFONT, 0, 0)
		self.valueedit = CreateWindowEx(0,"edit", None, win32con.WS_VSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_MULTILINE | win32con.ES_READONLY, 1, 1, 617, 425, self.hwnd, 0, self.hinst, None)
		win32gui.SendMessage(self.valueedit, win32con.WM_SETFONT, self.hfont, 0)
		
		clipval = ""
		if clipboard[0]["type"] == COMPOUND and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
			clipval += "{"
		elif clipboard[0]["type"] == LIST and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
			clipval += "["
		clipval += NBT2Command(Serialize(clipboard,0, TAG_Compound(), True if clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long)) else False))
		if clipboard[0]["type"] == COMPOUND and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
			clipval += "}"
		elif clipboard[0]["type"] == LIST and (clipboard[0]["name"] == "" or isinstance(clipboard[0]["name"], (int,long))):
			clipval += "]"
		clipval += "\0"
		SetText(self.valueedit,clipval.decode("unicode-escape"))
	
	def _RegisterWndClass(self):
		className = "ClipboardViewerClass"
		message_map = {}
		wc = win32gui.WNDCLASS()
		wc.SetDialogProc()
		wc.hInstance = self.hinst
		wc.lpszClassName = className
		wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
		wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
		wc.hbrBackground = win32con.COLOR_WINDOW + 1
		wc.lpfnWndProc = message_map
		wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
		icon_flags = win32con.LR_DEFAULTSIZE
		wc.hIcon=0

		try:
			classAtom = win32gui.RegisterClass(wc)
		except win32gui.error, err_info:
			if err_info.winerror!=winerror.ERROR_CLASS_ALREADY_EXISTS:
				raise
		return className

	def _GetDialogTemplate(self, dlgClassName):
		style = win32con.WS_BORDER | win32con.WS_VISIBLE | win32con.WS_CAPTION | win32con.WS_SYSMENU
		cs = win32con.WS_CHILD | win32con.WS_VISIBLE

		dlg = [ [self.title, (0, 0, 412, 262), style, None, (8, "MS Sans Serif"), None, dlgClassName], ]
		
		return dlg

class EditDialog(DialogBase):

	def __init__(self):
		super(EditDialog,self).__init__()
		self.title = "Edit Tag"

	def RangeCheck(self,val,nttype):
		retval = success = -1
		if nttype == LONG:
			try:
				retval = long(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to TAG_Long", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
		elif nttype == INT:
			try:
				retval = int(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to TAG_Int", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
			if retval > 2147483647:
				retval = 2147483647
			elif retval < -2147483648:
				retval = -2147483648
		elif nttype == SHORT:
			try:
				retval = int(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to TAG_Short", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
			if retval > 32767:
				retval = 32767
			elif retval < -32768:
				retval = -32768
		elif nttype == BYTE:
			try:
				retval = int(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to TAG_Byte", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
			if retval > 127:
				retval = 127
			elif retval < -128:
				retval = -128
		elif nttype == DOUBLE:
			try:
				retval = float(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to TAG_Double", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
		elif nttype == FLOAT:
			try:
				retval = float(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to TAG_Float", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
		elif nttype == INT_ARRAY:
			newarray = []
			for parts in val.split(","):
				newval, success = self.RangeCheck(parts,INT)
				if success == -1:
					return (-1,-1)
				newarray.append(str(newval))
			retval = ",".join(newarray)
		elif nttype == BYTE_ARRAY:
			newarray = []
			for parts in val.split(","):
				newval, success = self.RangeCheck(parts,UBYTE)
				if success == -1:
					return (-1,-1)
				newarray.append(str(newval))
			retval = ",".join(newarray)
		elif nttype == UBYTE:
			try:
				retval = int(val)
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Could not convert value \""+val[:50]+"\" to unsigned TAG_Byte", "Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return (retval, success)
			if retval > 255:
				retval = 255
			elif retval < 0:
				retval = 0
		return (retval, 1)

	def OnCommand(self, hwnd, msg, wparam, lparam):
		global tags, targettag, newtag
		id = win32api.LOWORD(wparam)
		if id == CDC_BUTTON_DONE:
			nameval = GetText(self.nameedit)
			if tags[tags[targettag]["parent"]]["type"] == COMPOUND:
				if tags[targettag]["name"] != nameval:
					for tag in tags[tags[targettag]["parent"]]["children"]:
						if tags[tag]["name"] == nameval:
							win32gui.MessageBox(self.hwnd, "There is already a \""+nameval+"\" tag! All tag names must be unique within a Compound tag!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
							return
			valval = GetText(self.valueedit)
			if self.Hex:
				valval = re.sub("[^0-9A-Fa-f,+-]","",valval)
				vals = valval.split(",")
				vals = ["0" if v == "" else v for v in vals]
				valval = unicode(",".join([str(int(v,16)) for v in vals]))
				
			if self.Formatted:
				valval = unicode(strcollapse(valval.decode("unicode-escape").split("\r\n")))
			else:
				valval = valval.decode("unicode-escape")
			for button, label in self.buttons:
				if win32gui.SendMessage(button, win32con.BM_GETCHECK, 0, 0):
					nttype = self.buttons.index((button,label))
					break
			if nttype in (COMPOUND, LIST):
				newval = 0
			elif nttype == STRING:
				newval = valval
			else:
				newval, result = self.RangeCheck(valval, nttype)
				if result == -1:
					return 1
			newtag = [nameval,newval,nttype]
			win32gui.EndDialog(self.hwnd, 1)
		elif id == CDC_FORMATTEXT:
			valval = GetText(self.valueedit).decode("unicode-escape")
			self.Formatted ^= True
			if not self.Formatted:
				SetText(self.valueedit,unicode(strcollapse(valval.split("\r\n"))))
			else:
				newvalue = ""
				if "{" in valval:
					mdatapos = valval.find("{")
					if mdatapos == 0:
						newvalue += "\r\n".join(strexplode(valval))
					else:
						newvalue += valval[:mdatapos]+"\r\n"+"\r\n".join(strexplode(valval[mdatapos:]))
				else:
					newvalue = valval
				SetText(self.valueedit,unicode(newvalue))
			win32gui.SetFocus(self.valueedit)
		elif id == CDC_HEX:
			valval = GetText(self.valueedit).decode("unicode-escape")
			self.Hex ^= True
			if self.Hex:
				valval = re.sub("[^0-9,+-]","",valval)
			else:
				valval = re.sub("[^0-9A-Fa-f,+-]","",valval)
			vals = valval.split(",")
			vals = ["0" if v == "" else v for v in vals]

			try:
				newval = [format(int(v),"X") if self.Hex else str(int(v,16)) for v in vals]
			except ValueError:
				win32gui.MessageBox(self.hwnd, "Unable to convert value!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				self.Hex ^= True
				win32gui.SendMessage(self.HexCheck, win32con.BM_SETCHECK, win32con.BST_CHECKED if self.Hex else win32con.BST_UNCHECKED, 0)
				return 1

			newval = unicode(",".join(newval))
		
			SetText(self.valueedit,unicode(newval))
			win32gui.SetFocus(self.valueedit)
		elif id == win32con.IDCANCEL:
			win32gui.EndDialog(self.hwnd, 0)
		elif id == CDC_SECTION:
			win32gui.SetFocus(self.valueedit)
			win32gui.SendMessage(self.valueedit, win32con.EM_REPLACESEL, 1, u"\xa7")
		elif id == CDC_INSERTTAB:
			win32gui.SetFocus(self.valueedit)
			win32gui.SendMessage(self.valueedit, win32con.EM_REPLACESEL, 1, "\t")
		elif id == CDC_SELECTALL:
			win32gui.SetFocus(self.valueedit)
			win32gui.SendMessage(self.valueedit, win32con.EM_SETSEL, 0, -1)
		elif id == CDC_BYTERADIO:
			valval = GetText(self.valueedit)
			if self.Hex:
				valval = re.sub("[^0-9A-Fa-f,+-]","",valval)
				vals = valval.split(",")
				vals = ["0" if v == "" else v for v in vals]
				newval = [str(int(v,16)) for v in vals]
				newval = unicode(",".join(newval))
				SetText(self.valueedit,newval)
				self.Hex = False
				win32gui.SendMessage(self.HexCheck, win32con.BM_SETCHECK, win32con.BST_UNCHECKED, 0)
				
			if self.Formatted:
				valval = unicode(strcollapse(valval.decode("unicode-escape").split("\r\n")))
				SetText(self.valueedit,valval)
				self.Formatted = False
				win32gui.SendMessage(self.FormatCheck, win32con.BM_SETCHECK, win32con.BST_UNCHECKED, 0)

			for button, label in self.buttons:
				if button == lparam:
					if self.buttons.index((button,label)) in (COMPOUND,LIST):
						win32gui.EnableWindow(self.valuelabel,False)
						win32gui.EnableWindow(self.valueedit,False)
						win32gui.EnableWindow(self.AllButton,False)
						win32gui.EnableWindow(self.TabButton,False)
						win32gui.EnableWindow(self.FormatCheck,False)
						win32gui.EnableWindow(self.SectionButton,False)

					else:
						win32gui.EnableWindow(self.valuelabel,True)
						win32gui.EnableWindow(self.valueedit,True)
						win32gui.EnableWindow(self.AllButton,True)

						if self.buttons.index((button,label)) == STRING:
							win32gui.SetWindowLong(self.valueedit, win32con.GWL_STYLE, win32con.WS_VSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_MULTILINE | win32con.ES_WANTRETURN)
							win32gui.EnableWindow(self.TabButton,True)
							win32gui.EnableWindow(self.FormatCheck,True)
							win32gui.EnableWindow(self.SectionButton,True)
						else:
							win32gui.SetWindowLong(self.valueedit, win32con.GWL_STYLE, win32con.WS_HSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_NUMBER | win32con.ES_AUTOHSCROLL)
							win32gui.EnableWindow(self.TabButton,False)
							win32gui.EnableWindow(self.FormatCheck,False)
							win32gui.EnableWindow(self.SectionButton,False)
					if self.buttons.index((button,label)) in (COMPOUND,LIST): #select the correct edit box and select/deselect text
						win32gui.SetFocus(self.nameedit)
						win32gui.SendMessage(self.nameedit, win32con.EM_SETSEL, 0, -1)
						win32gui.SendMessage(self.valueedit, win32con.EM_SETSEL, 0, 0)
					else:
						win32gui.SendMessage(self.nameedit, win32con.EM_SETSEL, 0, 0)
						win32gui.SetFocus(self.valueedit)
						if self.buttons.index((button,label)) != STRING:
							win32gui.SendMessage(self.valueedit, win32con.EM_SETSEL, 0, -1)
					if self.buttons.index((button,label)) in (BYTE,SHORT,INT,LONG,INT_ARRAY,BYTE_ARRAY):
						win32gui.EnableWindow(self.HexCheck,True)
					else:
						win32gui.EnableWindow(self.HexCheck,False)
					break
		return 1
			
	def DisableStuff(self):
		global tags, targettag
		if tags[tags[targettag]["parent"]]["type"] != LIST:
			SetText(self.nameedit,unicode(tags[targettag]["name"]))
		if tags[targettag]["type"] not in (COMPOUND, LIST):
			SetText(self.valueedit,unicode(tags[targettag]["value"]))
		for button, label in self.buttons:
			win32gui.SendMessage(button,win32con.BM_SETCHECK,False,None)
		win32gui.SendMessage(self.buttons[tags[targettag]["type"]][0],win32con.BM_SETCHECK,True,None)
		
		if tags[targettag]["type"] in (COMPOUND, LIST):
			win32gui.SetFocus(self.nameedit)
			win32gui.SendMessage(self.nameedit, win32con.EM_SETSEL, 0, -1)
			win32gui.EnableWindow(self.valuelabel,False)
			win32gui.EnableWindow(self.valueedit,False)
			win32gui.EnableWindow(self.AllButton,False)
			win32gui.EnableWindow(self.TabButton,False)
			win32gui.EnableWindow(self.FormatCheck,False)
			for button, label in self.buttons:
				if self.buttons.index((button,label)) == tags[targettag]["type"]:
					continue
				win32gui.EnableWindow(label,False)
				win32gui.EnableWindow(button,False)
		if tags[tags[targettag]["parent"]]["type"] == LIST:
			win32gui.SetFocus(self.valueedit)
			win32gui.SendMessage(self.valueedit, win32con.EM_SETSEL, 0, -1)
			win32gui.EnableWindow(self.namelabel,False)
			win32gui.EnableWindow(self.nameedit,False)
			win32gui.EnableWindow(self.AllButton,False)
			win32gui.EnableWindow(self.TabButton,False)
			win32gui.EnableWindow(self.FormatCheck,False)
			for button, label in self.buttons:
				if self.buttons.index((button,label)) == tags[targettag]["type"]:
					continue
				win32gui.EnableWindow(label,False)
				win32gui.EnableWindow(button,False)
		if tags[targettag]["type"] != STRING:
			win32gui.SetWindowLong(self.valueedit, win32con.GWL_STYLE, win32con.WS_HSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_NUMBER | win32con.ES_AUTOHSCROLL)
			win32gui.EnableWindow(self.TabButton,False)
			win32gui.EnableWindow(self.FormatCheck,False)
			win32gui.EnableWindow(self.SectionButton,False)
		else:
			win32gui.EnableWindow(self.AllButton,True)
			win32gui.EnableWindow(self.TabButton,True)
			win32gui.EnableWindow(self.FormatCheck,True)
			win32gui.EnableWindow(self.SectionButton,True)
			win32gui.SetWindowLong(self.valueedit, win32con.GWL_STYLE, win32con.WS_VSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_MULTILINE | win32con.ES_WANTRETURN)
			win32gui.SetFocus(self.valueedit)
		if tags[targettag]["type"] not in (COMPOUND, LIST, STRING):
			win32gui.SendMessage(self.valueedit,win32con.EM_SETSEL,0,-1)
			win32gui.SetFocus(self.valueedit)
		if tags[targettag]["type"] in (BYTE,SHORT,INT,LONG,INT_ARRAY,BYTE_ARRAY):
			win32gui.EnableWindow(self.HexCheck,True)
		else:
			win32gui.EnableWindow(self.HexCheck,False)
			
	def _SetupList(self):
		global tags, targettag
		self.groupBox = self.hwnd
		pathdir = os.path.join(mcplatform.filtersDir,"NBT_icons")
		if os.path.isdir(pathdir):
			icons = []
			for i in iconnames:
				icons.append(win32gui.LoadImage(0,os.path.join(pathdir,i),1,0,0,0x00000010))
		self.hfont = win32gui.SendMessage(self.hwnd, win32con.WM_GETFONT, 0, 0)
		self.buttons = []

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTORADIOBUTTON | win32con.BS_ICON | win32con.BS_RIGHTBUTTON
		br = CreateWindowEx(0,"BUTTON", None, child_style, 1, 1, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Compound", win32con.WS_CHILD | win32con.WS_VISIBLE, 33, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 1, 19, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_List", win32con.WS_CHILD | win32con.WS_VISIBLE, 33, 19, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))
		
		br = CreateWindowEx(0,"BUTTON", None, child_style, 120, 1, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Long", win32con.WS_CHILD | win32con.WS_VISIBLE, 152, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 120, 19, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Int", win32con.WS_CHILD | win32con.WS_VISIBLE, 152, 19, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))
		
		br = CreateWindowEx(0,"BUTTON", None, child_style, 214, 1, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Short", win32con.WS_CHILD | win32con.WS_VISIBLE, 246, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 214, 19, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Byte", win32con.WS_CHILD | win32con.WS_VISIBLE, 246, 19, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 308, 1, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Double", win32con.WS_CHILD | win32con.WS_VISIBLE, 341, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 308, 19, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Float", win32con.WS_CHILD | win32con.WS_VISIBLE, 341, 19, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 408, 1, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Int_Array", win32con.WS_CHILD | win32con.WS_VISIBLE, 440, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))
		
		br = CreateWindowEx(0,"BUTTON", None, child_style, 408, 19, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Byte_Array", win32con.WS_CHILD | win32con.WS_VISIBLE, 440, 19, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 525, 1, 31, 16, self.groupBox, CDC_BYTERADIO, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_String", win32con.WS_CHILD | win32con.WS_VISIBLE, 557, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.buttons.append((br,bl))
		win32gui.SendMessage(br, win32con.BM_SETCHECK, win32con.BST_CHECKED, 0)

		self.namelabel = CreateWindowEx(0,"static", "Tag Name:", win32con.WS_CHILD | win32con.WS_VISIBLE, 1, 43, 60, 16, self.hwnd, 0, self.hinst, None)
		self.nameedit = CreateWindowEx(0,"edit", None, win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL, 60, 40, 361, 20, self.hwnd, 0, self.hinst, None)
		win32gui.SendMessage(self.namelabel, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.SendMessage(self.nameedit, win32con.WM_SETFONT, self.hfont, 0)
		
		self.valuelabel = CreateWindowEx(0,"static", "Tag Value:", win32con.WS_CHILD | win32con.WS_VISIBLE, 1, 66, 58, 16, self.hwnd, 0, self.hinst, None)
		self.valueedit = CreateWindowEx(0,"edit", None, win32con.WS_VSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_MULTILINE | win32con.ES_WANTRETURN, 60, 63, 555, 359, self.hwnd, 0, self.hinst, None)
		win32gui.SendMessage(self.valuelabel, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.SendMessage(self.valueedit, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.SendMessage(self.valueedit, win32con.EM_LIMITTEXT, 0, 0)
		
		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX
		self.FormatCheck = CreateWindowEx(0,"BUTTON", "&Format Command", child_style, 426, 42, 100, 16, self.groupBox, CDC_FORMATTEXT, self.hinst, None)
		win32gui.SendMessage(self.FormatCheck, win32con.WM_SETFONT, self.hfont, 0)
		self.Formatted = False

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX
		self.HexCheck = CreateWindowEx(0,"BUTTON", "&Hexadecimal", child_style, 530, 42, 100, 16, self.groupBox, CDC_HEX, self.hinst, None)
		win32gui.SendMessage(self.HexCheck, win32con.WM_SETFONT, self.hfont, 0)
		self.Hex = False

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON
		self.AllButton = CreateWindowEx(0,"BUTTON", "Select &All", child_style, 2, 138, 55, 24, self.groupBox, CDC_SELECTALL, self.hinst, None)
		win32gui.SendMessage(self.AllButton, win32con.WM_SETFONT, self.hfont, 0)

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON
		self.TabButton = CreateWindowEx(0,"BUTTON", "&Tab", child_style, 2, 162, 55, 24, self.groupBox, CDC_INSERTTAB, self.hinst, None)
		win32gui.SendMessage(self.TabButton, win32con.WM_SETFONT, self.hfont, 0)

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON
		self.SectionButton = CreateWindowEx(0,"BUTTON", u"\xa7", child_style, 2, 186, 55, 24, self.groupBox, CDC_SECTION, self.hinst, None)
		win32gui.SendMessage(self.SectionButton, win32con.WM_SETFONT, self.hfont, 0)

		for button, label in self.buttons:
			win32gui.SendMessage(label, win32con.WM_SETFONT, self.hfont, 0)

		for i in xrange(len(self.buttons)):
			win32gui.SendMessage(self.buttons[i][0], win32con.BM_SETIMAGE, win32con.IMAGE_ICON, icons[i])

		self.DisableStuff()

	def _RegisterWndClass(self):
		className = "EditTagClass"
		message_map = {}
		wc = win32gui.WNDCLASS()
		wc.SetDialogProc()
		wc.hInstance = self.hinst
		wc.lpszClassName = className
		wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
		wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
		wc.hbrBackground = win32con.COLOR_WINDOW + 1
		wc.lpfnWndProc = message_map
		wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
		icon_flags = win32con.LR_DEFAULTSIZE
		wc.hIcon=0

		try:
			classAtom = win32gui.RegisterClass(wc)
		except win32gui.error, err_info:
			if err_info.winerror!=winerror.ERROR_CLASS_ALREADY_EXISTS:
				raise
		return className

	def _GetDialogTemplate(self, dlgClassName):
		style = win32con.WS_BORDER | win32con.WS_VISIBLE | win32con.WS_CAPTION | win32con.WS_SYSMENU
		cs = win32con.WS_CHILD | win32con.WS_VISIBLE

		dlg = [ [self.title, (0, 0, 412, 262), style, None, (8, "MS Sans Serif"), None, dlgClassName], ]
		s = cs | win32con.BS_PUSHBUTTON
		dlg.append([128, "&Done", CDC_BUTTON_DONE, (2, 53, 36, 14), s | win32con.BS_DEFPUSHBUTTON])
		dlg.append([128, "&Cancel", win32con.IDCANCEL, (2, 67, 36, 14), s])
		
		return dlg
		
	def _DoCreate(self, fn, hwnd):
		message_map = {
			win32con.WM_COMMAND: self.OnCommand,
			win32con.WM_NOTIFY: self.OnNotify,
			win32con.WM_INITDIALOG: self.OnInitDialog,
			win32con.WM_CLOSE: self.OnClose,
			win32con.WM_DESTROY: self.OnDestroy,
		}
		dlgClassName = self._RegisterWndClass()
		template = self._GetDialogTemplate(dlgClassName)
		return fn(self.hinst, template, hwnd, message_map)
		
	def Create(self, hwnd):
		return self._DoCreate(win32gui.DialogBoxIndirect, hwnd)

	def OnClose(self, hwnd, msg, wparam, lparam):
		win32gui.EndDialog(hwnd, 0)

class NewDialog(EditDialog):
	def __init__(self):
		super(NewDialog,self).__init__()
		self.title = "New Tag"
		
	def DisableStuff(self):
		global tags, targettag
		if tags[targettag]["type"] not in (COMPOUND, LIST):	#not scalar, so can't insert below
			if tags[tags[targettag]["parent"]]["type"] == COMPOUND:	#compounds can contain aggregate data types
				self.insertop = 0
				newtagtype = -1
				newtagname = True
			elif tags[tags[targettag]["parent"]]["type"] == LIST:	#lists can't
				disableall = True
				newtagname = False
				newtagtype = tags[targettag]["type"]
				self.insertop = 0
		else:	#inserting into child container
			if not tags[targettag]["children"] or tags[targettag]["type"] == COMPOUND:	#no children or is a compound, takes any tag type
				self.insertop = 1
				newtagtype = -1
				newtagname = True
			elif tags[targettag]["children"]:
				if tags[targettag]["type"] == LIST:
					self.insertop = 1
					newtagtype = tags[tags[targettag]["children"][0]]["type"]
					newtagname = False
					disableall = True

		if not newtagname:
			win32gui.EnableWindow(self.namelabel,False)
			win32gui.EnableWindow(self.nameedit,False)
		if newtagtype != -1:
			if newtagtype in (COMPOUND, LIST):
				win32gui.EnableWindow(self.valuelabel,False)
				win32gui.EnableWindow(self.valueedit,False)

			if newtagtype != STRING:
				win32gui.SetWindowLong(self.valueedit, win32con.GWL_STYLE, win32con.WS_HSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_NUMBER | win32con.ES_AUTOHSCROLL)
				win32gui.EnableWindow(self.TabButton,False)
				win32gui.EnableWindow(self.FormatCheck,False)
			else:
				win32gui.SetWindowLong(self.valueedit, win32con.GWL_STYLE, win32con.WS_VSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_MULTILINE | win32con.ES_WANTRETURN)
				win32gui.SetFocus(self.valueedit)

			if disableall:
				for button, label in self.buttons:
					if self.buttons.index((button,label)) == newtagtype:
						continue
					win32gui.EnableWindow(label,False)
					win32gui.EnableWindow(button,False)
			win32gui.SendMessage(self.buttons[newtagtype][0],win32con.BM_SETCHECK,True,None)
		
	def OnCommand(self, hwnd, msg, wparam, lparam):
		global tags, targettag, newtag, newtagtype
		id = win32api.LOWORD(wparam)
		if id == CDC_BUTTON_DONE:
			nameval = GetText(self.nameedit)
			if self.insertop:
				if tags[targettag]["type"] == COMPOUND:
					if nameval == "":
						win32gui.MessageBox(self.hwnd, "No name specified!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
						return
					for tag in tags[targettag]["children"]:
						if tags[tag]["name"] == nameval:
							win32gui.MessageBox(self.hwnd, "There is already a \""+nameval+"\" tag! All tag names must be unique within a Compound tag!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
							return
			else:
				if tags[tags[targettag]["parent"]]["type"] == COMPOUND:
					if nameval == "":
						win32gui.MessageBox(self.hwnd, "No name specified!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
						return
					for tag in tags[tags[targettag]["parent"]]["children"]:
						if tags[tag]["name"] == nameval:
							win32gui.MessageBox(self.hwnd, "There is already a \""+nameval+"\" tag! All tag names must be unique within a Compound tag!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
							return
			valval = GetText(self.valueedit)
			if self.Formatted:
				valval = unicode(strcollapse(valval.decode("unicode-escape").split("\n")))
			else:
				valval = valval.decode("unicode-escape")
			for button, label in self.buttons:
				if win32gui.SendMessage(button, win32con.BM_GETCHECK, 0, 0):
					nttype = self.buttons.index((button,label))
					break
			else:
				win32gui.MessageBox(self.hwnd, "No tag type specified!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
				return
			if nttype in (COMPOUND, LIST):
				newval = 0
			elif nttype == STRING:
				newval = valval
			else:
				newval, result = self.RangeCheck(valval, nttype)
				if result == -1:
					return 1
			newtag = [nameval,newval,nttype,self.insertop]
			win32gui.EndDialog(self.hwnd, 1)
		else:
			super(NewDialog,self).OnCommand(hwnd, msg, wparam, lparam)
		return 1

class PesterDialog(EditDialog):
	def __init__(self):
		super(PesterDialog,self).__init__()
		self.title = "Input New Tag Name"

	def DisableStuff(self):
		win32gui.EnableWindow(self.namelabel,True)
		win32gui.EnableWindow(self.nameedit,True)
		win32gui.EnableWindow(self.valuelabel,False)
		win32gui.EnableWindow(self.valueedit,False)
		win32gui.EnableWindow(self.AllButton,False)
		win32gui.EnableWindow(self.TabButton,False)
		win32gui.EnableWindow(self.FormatCheck,False)
		for button, label in self.buttons:
			win32gui.EnableWindow(label,False)
			win32gui.EnableWindow(button,False)

	def OnCommand(self, hwnd, msg, wparam, lparam):
		global newtag, targettag
		id = win32api.LOWORD(wparam)
		if id == CDC_BUTTON_DONE:
			insertop = True
			nameval = GetText(self.nameedit)
			if tags[targettag]["type"] == COMPOUND:
				if nameval == "":
					win32gui.MessageBox(self.hwnd, "No name specified!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
					return
				for tag in tags[targettag]["children"]:
					if tags[tag]["name"] == nameval:
						win32gui.MessageBox(self.hwnd, "There is already a \""+nameval+"\" tag! All tag names must be unique within a Compound tag!","Error", win32con.MB_OK | win32con.MB_ICONEXCLAMATION)
						return
			newtag = [nameval,insertop]
			win32gui.EndDialog(self.hwnd, 1)
		else:
			super(PesterDialog,self).OnCommand(hwnd, msg, wparam, lparam)
		return 1

class FindDialog(EditDialog):
	def __init__(self):
		super(FindDialog,self).__init__()
		self.title = "Find"

	def OnCommand(self, hwnd, msg, wparam, lparam):
		global tags, targettag, newtag, TreeHandle
		id = win32api.LOWORD(wparam)
		if id == win32con.IDCANCEL:
			FindHandle = None
			win32gui.EndDialog(self.hwnd, 0)
		elif id == IDC_BUTTON_FIND:
			if targettag == None:
				targettag = 0
			taglist = []
			for button, label in self.checks:
				if win32gui.SendMessage(button, win32con.BM_GETCHECK, 0, 0):
					taglist.append(self.checks.index((button,label)))
			if not taglist:
				taglist = range(11)
			name = GetText(self.findnameedit)
			if not self.DoMatchCase:
				name = name.upper()
			value = GetText(self.findvalueedit)
			if not self.DoMatchCase:
				value = value.upper()
			found = self.FindTag(name, value, taglist, self.DoMatchCase, self.ExactName, self.ExactValue, targettag, targettag)
			if found != -1:
				win32gui.SendMessage(TreeHandle, commctrl.TVM_EXPAND, commctrl.TVE_EXPAND, tags[found]["hitem"])
				win32gui.PostMessage(TreeHandle, commctrl.TVM_SELECTITEM, commctrl.TVGN_CARET, tags[found]["hitem"])
				win32gui.SetFocus(TreeHandle)
			else:
				win32gui.MessageBox(self.hwnd, "No matching item found.", "404", win32con.MB_OK | win32con.MB_ICONINFORMATION)
			
		elif id == CDC_EXACT_NAME:
			self.ExactName ^= True
		elif id == CDC_EXACT_VALUE:
			self.ExactValue ^= True
		elif id == CDC_MATCH_CASE:
			self.DoMatchCase ^= True
		return 1
	
	def FindTag(self,name, value, taglist, MatchCase, ExactName, ExactValue, item, start):
		global tags
		if item == -1:
			return -1
		result = self.SearchDown(name, value, taglist, MatchCase, ExactName, ExactValue, item, start)
		if result != -1:
			return result
		return self.FindTag(name, value, taglist, MatchCase, ExactName, ExactValue, self.SearchUp(item), start)

	def TestItem(self,name, value, taglist, MatchCase, ExactName, ExactValue, item):
		global tags
		if item == -1:
			return -1
		nameval = tags[item]["name"]
		if isinstance(nameval, (int, long)):
			nameval = ""
		valval = unicode(tags[item]["value"])
		if not MatchCase:
			nameval = nameval.upper()
			valval = valval.upper()
			
		if tags[item]["type"] in taglist:
			if ExactName:
				if name == "":
					if value == "":
						return item
					if ExactValue:
						if valval == value:
							return item
					else:
						if value in valval:
							return item
				elif nameval == name:
					if value == "":
						return item
					if tags[item]["type"] in (COMPOUND,LIST):
						return item
					if ExactValue:
						if valval == value:
							return item
					else:
						if value in valval:
							return item
			else:
				if name == "":
					if value == "":
						return item
					if ExactValue:
						if valval == value:
							return item
					else:
						if value in valval:
							return item
				elif name in nameval:
					if value == "":
						return item
					if tags[item]["type"] in (COMPOUND,LIST):
						return item
					if ExactValue:
						if valval == value:
							return item
					else:
						if value in valval:
							return item
		return -1

	def SearchDown(self,name, value, taglist, MatchCase, ExactName, ExactValue, item, start):
		global tags
		if item == -1:
			return -1
		if item == start: #crappy hack to search after the currently-selected item.
			result = -1
		else:
			result = self.TestItem(name, value, taglist, MatchCase, ExactName, ExactValue, item)
		if result != -1:
			return result
		else:
			for c in tags[item]["children"]:
				result = self.SearchDown(name, value, taglist, MatchCase, ExactName, ExactValue, c, start)
				if result != -1:
					return result
			else:
				return -1

	def SearchUp(self,item):
		global tags
		if item == -1:
			return -1
		parent = tags[item]["parent"]
		if parent == None or parent == "":
			return -1
		if tags[parent]["children"].index(item) != len(tags[parent]["children"])-1:
			return tags[parent]["children"][tags[parent]["children"].index(item)+1]
		else:
			return self.SearchUp(parent)

	def DisableStuff(self):
		return
			
	def _SetupList(self):
		global tags, targettag, FindHandle
		FindHandle = self.hwnd
		self.groupBox = self.hwnd
		pathdir = os.path.join(mcplatform.filtersDir,"NBT_icons")
		if os.path.isdir(pathdir):
			icons = []
			for i in iconnames:
				icons.append(win32gui.LoadImage(0,os.path.join(pathdir,i),1,0,0,0x00000010))
		self.hfont = win32gui.SendMessage(self.hwnd, win32con.WM_GETFONT, 0, 0)
		self.checks = []

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX | win32con.BS_ICON | win32con.BS_RIGHTBUTTON
		br = CreateWindowEx(0,"BUTTON", None, child_style, 1, 1, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Compound", win32con.WS_CHILD | win32con.WS_VISIBLE, 33, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 1, 18, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_List", win32con.WS_CHILD | win32con.WS_VISIBLE, 33, 18, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))
		
		br = CreateWindowEx(0,"BUTTON", None, child_style, 120, 1, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Long", win32con.WS_CHILD | win32con.WS_VISIBLE, 152, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 120, 18, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Int", win32con.WS_CHILD | win32con.WS_VISIBLE, 152, 18, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))
		
		br = CreateWindowEx(0,"BUTTON", None, child_style, 214, 1, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Short", win32con.WS_CHILD | win32con.WS_VISIBLE, 246, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 214, 18, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Byte", win32con.WS_CHILD | win32con.WS_VISIBLE, 246, 18, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 308, 1, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Double", win32con.WS_CHILD | win32con.WS_VISIBLE, 341, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 308, 18, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Float", win32con.WS_CHILD | win32con.WS_VISIBLE, 341, 18, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 408, 1, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Int_Array", win32con.WS_CHILD | win32con.WS_VISIBLE, 440, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))
		
		br = CreateWindowEx(0,"BUTTON", None, child_style, 408, 18, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_Byte_Array", win32con.WS_CHILD | win32con.WS_VISIBLE, 440, 18, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		br = CreateWindowEx(0,"BUTTON", None, child_style, 525, 1, 31, 16, self.groupBox, CDC_BYTECHECK, self.hinst, None)
		bl = CreateWindowEx(0,"static", "TAG_String", win32con.WS_CHILD | win32con.WS_VISIBLE, 557, 1, 80, 16, self.groupBox, 0, self.hinst, None)
		self.checks.append((br,bl))

		self.findnamelabel = CreateWindowEx(0,"static", "Name:", win32con.WS_CHILD | win32con.WS_VISIBLE, 5, 43, 30, 16, self.hwnd, 0, self.hinst, None)
		self.findnameedit = CreateWindowEx(0,"edit", None, win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL, 40, 40, 490, 20, self.hwnd, 0, self.hinst, None)
		win32gui.SendMessage(self.findnamelabel, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.SendMessage(self.findnameedit, win32con.WM_SETFONT, self.hfont, 0)
		
		self.findvaluelabel = CreateWindowEx(0,"static", "Value:", win32con.WS_CHILD | win32con.WS_VISIBLE, 5, 66, 30, 16, self.hwnd, 0, self.hinst, None)
		self.findvalueedit = CreateWindowEx(0,"edit", None, win32con.WS_VSCROLL | win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER | win32con.ES_NOHIDESEL | win32con.ES_MULTILINE | win32con.ES_WANTRETURN, 40, 63, 490, 75, self.hwnd, 0, self.hinst, None)
		win32gui.SendMessage(self.findvaluelabel, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.SendMessage(self.findvalueedit, win32con.WM_SETFONT, self.hfont, 0)
		win32gui.SendMessage(self.findvalueedit, win32con.EM_LIMITTEXT, 0, 0)

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX
		self.NameExact = CreateWindowEx(0,"BUTTON", "Exact Match", child_style, 533, 42, 75, 16, self.groupBox, CDC_EXACT_NAME, self.hinst, None)
		win32gui.SendMessage(self.NameExact, win32con.WM_SETFONT, self.hfont, 0)
		self.ExactName = False
		
		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX
		self.ValueExact = CreateWindowEx(0,"BUTTON", "Exact Match", child_style, 533, 65, 75, 16, self.groupBox, CDC_EXACT_VALUE, self.hinst, None)
		win32gui.SendMessage(self.ValueExact, win32con.WM_SETFONT, self.hfont, 0)
		self.ExactValue = False

		child_style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX
		self.MatchCase = CreateWindowEx(0,"BUTTON", "Match Case", child_style, 533, 122, 75, 16, self.groupBox, CDC_MATCH_CASE, self.hinst, None)
		win32gui.SendMessage(self.MatchCase, win32con.WM_SETFONT, self.hfont, 0)
		self.DoMatchCase = False
		
		for button, label in self.checks:
			win32gui.SendMessage(label, win32con.WM_SETFONT, self.hfont, 0)

		for i in xrange(len(self.checks)):
			win32gui.SendMessage(self.checks[i][0], win32con.BM_SETIMAGE, win32con.IMAGE_ICON, icons[i])

	def _RegisterWndClass(self):
		className = "FindTagClass"
		message_map = {}
		wc = win32gui.WNDCLASS()
		wc.SetDialogProc()
		wc.hInstance = self.hinst
		wc.lpszClassName = className
		wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
		wc.hCursor = win32gui.LoadCursor( 0, win32con.IDC_ARROW )
		wc.hbrBackground = win32con.COLOR_WINDOW + 1
		wc.lpfnWndProc = message_map
		wc.cbWndExtra = win32con.DLGWINDOWEXTRA + struct.calcsize("Pi")
		icon_flags = win32con.LR_DEFAULTSIZE
		wc.hIcon=0

		try:
			classAtom = win32gui.RegisterClass(wc)
		except win32gui.error, err_info:
			if err_info.winerror!=winerror.ERROR_CLASS_ALREADY_EXISTS:
				raise
		return className

	def _GetDialogTemplate(self, dlgClassName):
		style = win32con.WS_BORDER | win32con.WS_VISIBLE | win32con.WS_CAPTION | win32con.WS_SYSMENU
		cs = win32con.WS_CHILD | win32con.WS_VISIBLE

		dlg = [ [self.title, (0, 0, 412, 85), style, win32con.WS_EX_TOPMOST, (8, "MS Sans Serif"), None, dlgClassName], ]
		s = cs | win32con.BS_PUSHBUTTON
		dlg.append([128, "&Find Next", IDC_BUTTON_FIND, (355, 60, 55, 14), s | win32con.BS_DEFPUSHBUTTON])
		dlg.append([128, "&Close", win32con.IDCANCEL, (1, 70, 23, 14), s])
		
		return dlg
		
	def _DoCreate(self, fn, hwnd):
		message_map = {
			win32con.WM_COMMAND: self.OnCommand,
			win32con.WM_NOTIFY: self.OnNotify,
			win32con.WM_INITDIALOG: self.OnInitDialog,
			win32con.WM_CLOSE: self.OnClose,
			win32con.WM_DESTROY: self.OnClose,
		}
		dlgClassName = self._RegisterWndClass()
		template = self._GetDialogTemplate(dlgClassName)
		return fn(self.hinst, template, hwnd, message_map)
		
	def Create(self, hwnd):
		return self._DoCreate(win32gui.DialogBoxIndirect, hwnd)

	def OnClose(self, hwnd, msg, wparam, lparam):
		global FindHandle
		FindHandle = None
		win32gui.EndDialog(hwnd, 0)


def NewTag(name, value, id, type, hitem, parent, children):
	return {"name":name,"value":value,"id":id,"type":type,"hitem":hitem,"parent":parent,"children":children}

def Deserialize(obj, tag_num):
	global tags
	if type(obj) is TAG_Compound:
		for tag in sorted(obj.keys(),key=lambda s: s.lower()):
			if type(obj[tag]) in (TAG_Compound, TAG_List):
				new_tag = GetID()
				tags[new_tag] = NewTag(tag,0,new_tag,tagtypes[type(obj[tag])],None,tag_num,[])
				tags[tag_num]["children"].append(new_tag)
				Deserialize(obj[tag],new_tag)
			elif type(obj[tag]) in (TAG_Byte_Array, TAG_Int_Array):
				new_tag = GetID()
				tags[new_tag] = NewTag(tag,",".join(obj[tag].value.astype("str")),new_tag,tagtypes[type(obj[tag])],None,tag_num,[])
				tags[tag_num]["children"].append(new_tag)
			else:
				new_tag = GetID()
				tags[new_tag] = NewTag(tag,obj[tag].value,new_tag,tagtypes[type(obj[tag])],None,tag_num,[])
				tags[tag_num]["children"].append(new_tag)
	elif type(obj) is TAG_List:
		for index in range(0,len(obj)):
			if type(obj[index]) in (TAG_Compound, TAG_List):
				new_tag = GetID()
				tags[new_tag] = NewTag(index,0,new_tag,tagtypes[type(obj[index])],None,tag_num,[])
				tags[tag_num]["children"].append(new_tag)
				Deserialize(obj[index],new_tag)
			elif type(obj[index]) in (TAG_Byte_Array, TAG_Int_Array):
				new_tag = GetID()
				tags[new_tag] = NewTag(index,",".join(obj[index].value.astype("str")),new_tag,tagtypes[type(obj[index])],None,tag_num,[])
				tags[tag_num]["children"].append(new_tag)
			else:
				new_tag = GetID()
				tags[new_tag] = NewTag(index,obj[index].value,new_tag,tagtypes[type(obj[index])],None,tag_num,[])
				tags[tag_num]["children"].append(new_tag)

def NBT_Tag(type, value):
	if type == COMPOUND:
		return TAG_Compound()
	elif type == LIST:
		return TAG_List()
	elif type == BYTE_ARRAY:
		return TAG_Byte_Array(value)
	elif type == INT_ARRAY:
		return TAG_Int_Array(value)
	elif type == STRING:
		return TAG_String(value)
	elif type == LONG:
		return TAG_Long(value)
	elif type == INT:
		return TAG_Int(value)
	elif type == SHORT:
		return TAG_Short(value)
	elif type == BYTE:
		return TAG_Byte(value)
	elif type == DOUBLE:
		return TAG_Double(value)
	elif type == FLOAT:
		return TAG_Float(value)

def GetNBT(obj):
	global tags
	entlist = TAG_List()
	cmpnd = TAG_Compound()
	if "children" in obj:
		for o in obj["children"]:
			retval = Serialize(tags,o,cmpnd)
			newervar = deepcopy(retval)
			entlist.append(newervar)
			del newervar
	return entlist
		
def Serialize(tree,obj,nbt,scalar=False):
	if tree[obj]["type"] in (COMPOUND, LIST):
		if isinstance(tree[obj]["name"], (int,long)):
			nbt = NBT_Tag(tree[obj]["type"],0)
			nextnbt = nbt
		else:
			nbt[tree[obj]["name"]] = NBT_Tag(tree[obj]["type"],0)
			nextnbt = nbt[tree[obj]["name"]]
		if tree[obj]["children"]:
			if tree[obj]["type"] == COMPOUND:
				for o in tree[obj]["children"]:
					nextnbt = Serialize(tree,o,nextnbt)
			elif tree[obj]["type"] == LIST:
				for o in tree[obj]["children"]:
					nbt[tree[obj]["name"]].append(Serialize(tree,o,0,True))
			elif tree[obj]["type"] in (BYTE_ARRAY, INT_ARRAY):
				intbytearray = tree[obj]["value"]
				intbytearray = re.sub("[^0-9,+-]","",intbytearray)
				if tree[obj]["type"] == INT_ARRAY:
					nbt[tree[obj]["name"]] = NBT_Tag(tree[obj]["type"],numpy.array(intbytearray.split(","),dtype=">u4"))
				else:
					nbt[tree[obj]["name"]] = NBT_Tag(tree[obj]["type"],numpy.array(intbytearray.split(","),dtype="uint8"))
	elif tree[obj]["type"] in (BYTE_ARRAY, INT_ARRAY):
		intbytearray = tree[obj]["value"]
		intbytearray = re.sub("[^0-9,+-]","",intbytearray)
		if tree[obj]["type"] == INT_ARRAY:
			nbt[tree[obj]["name"]] = NBT_Tag(tree[obj]["type"],numpy.array(intbytearray.split(","),dtype=">u4"))
		else:
			nbt[tree[obj]["name"]] = NBT_Tag(tree[obj]["type"],numpy.array(intbytearray.split(","),dtype="uint8"))
	else:
		if scalar:
			return NBT_Tag(tree[obj]["type"],tree[obj]["value"])
		nbt[tree[obj]["name"]] = NBT_Tag(tree[obj]["type"],tree[obj]["value"])
	return nbt
	
def GetPosition(value):
	global tags
	newlist = []
	x = y = z = 0
	if tags[value]["type"] == COMPOUND:
		for a in tags[value]["children"]:
			if tags[a]["name"] == "x":
				x = tags[a]["value"]
			elif tags[a]["name"] == "y":
				y = tags[a]["value"]
			elif tags[a]["name"] == "z":
				z = tags[a]["value"]
			elif tags[a]["name"] == "Pos":
				(x,y,z) = GetPosition(a)
	elif tags[value]["type"] == LIST:
		x = tags[tags[value]["children"][0]]["value"]
		y = tags[tags[value]["children"][1]]["value"]
		z = tags[tags[value]["children"][2]]["value"]
	return (x,y,z)

def perform(level, box, options):
	global idcounter, clipboard, tags, FindHandle, TreeHandle
	FindHandle = None
	TreeHandle = None
	tileentstodelete = []
	entstodelete = []
	tickstodelete = []
	tags = {}
	if options["Edit..."] == "Selection":
		tags[0] = deepcopy(template)
		tags[0]["type"] = COMPOUND
		tags[0]["name"] = "Selection: ("+str(box.minx)+", "+str(box.miny)+", "+str(box.minz)+") to ("+str(box.maxx-1)+", "+str(box.maxy-1)+", "+str(box.maxz-1)+")"
		tags[0]["children"] = [1,2,3]
		tags[0]["id"] = 0
		
		tags[1] = deepcopy(template)
		tags[1]["type"] = LIST
		tags[1]["name"] = "TileEntities"
		tags[1]["parent"] = 0
		tags[1]["id"] = 1
		
		tags[2] = deepcopy(template)
		tags[2]["type"] = LIST
		tags[2]["name"] = "Entities"
		tags[2]["parent"] = 0
		tags[2]["id"] = 2
		
		tags[3] = deepcopy(template)
		tags[3]["type"] = LIST
		tags[3]["name"] = "TileTicks"
		tags[3]["parent"] = 0
		tags[3]["id"] = 3
		idcounter = 3

		for (chunk, _, _) in level.getChunkSlices(box):
			for e in chunk.TileEntities:
				x = e["x"].value
				y = e["y"].value
				z = e["z"].value
				if (x,y,z) in box:
					tileentstodelete.append((chunk,e))
					new_tag = GetID()
					tags[new_tag] = NewTag(0,None,new_tag,COMPOUND,None,1,[])
					tags[1]["children"].append(new_tag)
					Deserialize(e, new_tag)
			for e in chunk.Entities:
				x = e["Pos"][0].value
				y = e["Pos"][1].value
				z = e["Pos"][2].value
				if (x,y,z) in box:
					entstodelete.append((chunk,e))
					new_tag = GetID()
					tags[new_tag] = NewTag(0,None,new_tag,COMPOUND,None,2,[])
					tags[2]["children"].append(new_tag)
					Deserialize(e, new_tag)
			if level.gamePlatform != 'PE':
				if "TileTicks" in chunk.root_tag["Level"]:
					for e in chunk.root_tag["Level"]["TileTicks"]:
						x = e["x"].value
						y = e["y"].value
						z = e["z"].value
						if (x,y,z) in box:
							tickstodelete.append((chunk,e))
							new_tag = GetID()
							tags[new_tag] = NewTag(0,None,new_tag,COMPOUND,None,3,[])
							tags[3]["children"].append(new_tag)
							Deserialize(e, new_tag)
		tags[1]["children"] = sorted(tags[1]["children"], key=lambda x: GetPosition(x))
		tags[2]["children"] = sorted(tags[2]["children"], key=lambda x: GetPosition(x))
		tags[3]["children"] = sorted(tags[3]["children"], key=lambda x: GetPosition(x))

		if not CreateDialog(win32gui.GetForegroundWindow()):
			raise Exception("Edit operation was canceled; no changes were made.")
		if 1 in tags:
			tileentities = GetNBT(tags[1])
		else:
			tileentities = []
		if 2 in tags:
			entities = GetNBT(tags[2])
		else:
			entities = []
		if 3 in tags:
			tick = GetNBT(tags[3])
		else:
			tick = []

		for (chunk, entity) in tileentstodelete:
			chunk.TileEntities.remove(entity)
			chunk.dirty = True
		for (chunk, entity) in entstodelete:
			chunk.Entities.remove(entity)
			chunk.dirty = True
		if level.gamePlatform != 'PE':
			for (chunk, entity) in tickstodelete:
				chunk.root_tag["Level"]["TileTicks"].remove(entity)
				chunk.dirty = True
			
		for te in tileentities:
			if "x" in te and "y" in te and "z" in te:
				x = te["x"].value
				z = te["z"].value
				chunk = level.getChunk(x>>4, z>>4)
				chunk.TileEntities.append(te)
				chunk.dirty = True
		for e in entities:
			if "Pos" in e:
				if len(e["Pos"]) >= 3:
					x = e["Pos"][0].value
					z = e["Pos"][2].value
					x = int(x)>>4
					z = int(z)>>4
					chunk = level.getChunk(x, z)
					chunk.Entities.append(e)
					chunk.dirty = True
		if level.gamePlatform != 'PE':
			for t in tick:
				if "x" in t and "y" in t and "z" in t:
					x = t["x"].value
					z = t["z"].value
					chunk = level.getChunk(x>>4, z>>4)
					if "TileTicks" not in chunk.root_tag["Level"]:
						chunk.root_tag["Level"]["TileTicks"] = TAG_List()
					chunk.root_tag["Level"]["TileTicks"].append(t)
					chunk.dirty = True
	elif options["Edit..."] == "level.dat":
		tags[0] = deepcopy(template)
		tags[0]["type"] = COMPOUND
		tags[0]["name"] = "level.dat"
		idcounter = 0
		Deserialize(level.root_tag, 0)
		if not CreateDialog(win32gui.GetForegroundWindow()):
			raise Exception("Edit operation was canceled; no changes were made.")
		level.root_tag = deepcopy(Serialize(tags,1,TAG_Compound()))
	else:
		filename = mcplatform.askOpenFile(title="Select a Schematic or Dat File...", schematics=False)
		if filename == None:
			raise Exception("No file name provided.")

		if filename:
			buf = file(filename, "rb")
		if hasattr(buf, "read"):
			buf = buf.read()

		compressed = True
		try:
			buf = gzip.GzipFile(fileobj=StringIO(buf)).read()
		except IOError, zlib.error:
			compressed = False

		if isinstance(buf, str):
			buf = numpy.fromstring(buf, 'uint8')
		data = buf

		if not len(data):
			raise nbt.NBTFormatError("Asked to load root tag of zero length")

		tag_type = data[0]
		if tag_type != 10:
			raise nbt.NBTFormatError("Incorrectly formatted data file!")
			
		tags[0] = deepcopy(template)
		tags[0]["type"] = COMPOUND
		tags[0]["name"] = filename
		idcounter = 0
		Deserialize(nbt.load(filename), 0)
		if not CreateDialog(win32gui.GetForegroundWindow()):
			raise Exception("Edit operation was canceled; no changes were made.")
		tags[0]["name"] = 0
		filename = mcplatform.askSaveFile(os.path.split(filename)[0], "Save File...", "", "File\0*.*\0\0", os.path.basename(filename))
		if filename == None:
			raise Exception("No file name provided.")
		data_file = deepcopy(Serialize(tags,0,TAG_Compound()))
		data_file.save(filename,compressed)
		raise Exception("File Saved.")
