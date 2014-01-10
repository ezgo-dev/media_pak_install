#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import os
import getpass
import sys
username = getpass.getuser()

WELCOME_SIZE = 13000
IMAGE_SIZE = 60
TITLE_SIZE = 13000
MSG_SIZE = 13000

BG_COLOR = '#7AD9F6'
#BG_COLOR = '#94EFF4'

current_check_button = 0
total_check_button = 2
check_status = [True]*total_check_button
install_command = []

sh_file = '/home/'+username+'/.media_pak_install.sh'
dont_show_file = '/home/'+username+"/.media_pak_install.dont_show"
"""
dont_show_file 這個檔案若存在
就不會開啟本程式
"""

"""
sudo wget --output-document=/etc/apt/sources.list.d/medibuntu.list http://www.medibuntu.org/sources.list.d/$(lsb_release -cs).list && sudo apt-get --quiet update && sudo apt-get -y --force-yes --quiet --allow-unauthenticated install medibuntu-keyring && sudo apt-get --quiet update

sudo apt-get -y --force-yes install app-install-data-medibuntu apport-hooks-medibuntu
"""

def checkInstalled(pak_name):
	ret = os.system('dpkg --get-selections '+pak_name+' | grep "install"')
	if ret == 0:
		ret = os.system('dpkg --get-selections '+pak_name+' | grep "deinstall"')
		if ret == 0:
			return False
		#installed
		return True
	else:
		#not install yet
		return False


def check_button_callback( widget, data ):
	global check_status
	check_status[data] = not check_status[data]
	#print widget
	#print data
		

def newImageBox( image_path, title, msg, pak_name ):
	global check_status
	global current_check_button
	#[left]
	#check button
	button = gtk.CheckButton()
	button.set_active(check_status[current_check_button])
	button.connect("clicked", check_button_callback, current_check_button)
	button.set_border_width(11)
	button.show()
	
	#installed img
	installed_image = gtk.Image()
	pixbuf = gtk.gdk.pixbuf_new_from_file('./installed.png')
	scaled_buf = pixbuf.scale_simple(42,42,gtk.gdk.INTERP_BILINEAR)
	installed_image.set_from_pixbuf(scaled_buf)
	installed_image.show()
	#installed msg
	installed_label = gtk.Label('<span size="12000">'+'已安裝'+'</span>')
	installed_label.set_use_markup(True)
	installed_label.show()
	
	image = gtk.Image()
	pixbuf = gtk.gdk.pixbuf_new_from_file(image_path)
	scaled_buf = pixbuf.scale_simple(IMAGE_SIZE,IMAGE_SIZE,gtk.gdk.INTERP_BILINEAR)
	image.set_from_pixbuf(scaled_buf)
	image.show()
	
	#[right]
	frame = gtk.Frame(title)
	frame.set_label_align(0.05, 0.5)
	frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
	
	label = gtk.Label('<span size="'+str(MSG_SIZE)+'">'+msg+'</span>')
	label.set_use_markup(True)
	label.show()
	frame.add(label)

	label = gtk.Label('<span size="'+str(TITLE_SIZE)+'">'+title+'</span>')
	label.set_use_markup(True)
	label.show()
	frame.set_label_widget(label)

	
	frame.show()

	#[box]
	box = gtk.HBox(homogeneous=False)
	print 'check package status:', pak_name
	if( checkInstalled(pak_name) ):
		#button.set_sensitive(False)
		#box.pack_start(installed_image, expand=False, fill=True, padding=0)
		box.pack_start(installed_label, expand=False, fill=False, padding=10)
		button.set_active(False)
	else:
		box.pack_start(button, expand=False, fill=False, padding=10)
	#box.pack_start(button, expand=False, fill=False, padding=10)
	
	box.pack_start(image, expand=False, fill=True, padding=0)
	box.pack_start(frame, fill=True, padding=10)
	box.show()

	current_check_button += 1
	return box

def dontshow_button_callback( widget, data ):
	global dont_show_file
	if os.path.exists(dont_show_file):
		os.system('rm -f '+dont_show_file)
	else:
		os.system('touch '+dont_show_file)

class FlashInstall:
	def delete_event(self, widget, event, data=None):
		#self.ed.window.show_all()
		gtk.main_quit()
		return False
		
	def destroy_event(self, widget, data=None):
		#self.ed.window.show_all()
		gtk.main_quit()
		return False

	def apply_press_callback( self, widget, data ):
		global check_status
		global install_command
		global sh_file

		select_count = check_status.count(True)
		#print check_status
		#print select_count
		if select_count==0 :
			gtk.main_quit()
			return
		select_count += 1
		data.window.set_visible(False)
		now_bar_pos = 0
		
		
		#[確認能連上網路，才繼續往下]
		bash_to_exe = """
		ping -c 1 8.8.8.8 > /dev/null
		if [ $? != 0 ]; then
			#zenity --info --text 安裝失敗：無法連上網路
			kdialog --error 安裝失敗：無法連上網路
			exit 1
		fi
		exit 0
		"""
		rev = os.system( bash_to_exe )
		if rev != 0 :
			gtk.main_quit()
			return
		
		bash_to_exe =''
		
		bash_to_exe += """
		prog="/usr/lib/`uname -i`-linux-gnu/qt4/bin/qdbus"
		ure_installed=-1
		libdvdcss2_installed=-1
		"""
		
		bash_to_exe += "kdialog --msgbox 請在安裝前確定連上網路，並關閉瀏覽器及影音相關軟體\n"
		#[pre_install]
		bash_to_exe += 'echo "update packages"\n'
		bash_to_exe += 'dbusRef=`kdialog --progressbar "更新套件來源..." --title "安裝多媒體套件" ' + str(select_count) + '`\n'
		bash_to_exe += 'dpkg --configure -a\n'
		bash_to_exe += "apt-get update >&2\n"
		now_bar_pos += 1
		bash_to_exe += '$prog $dbusRef Set "" value '+str(now_bar_pos)+'\n'
		
		bash_to_exe += '$prog $dbusRef setLabelText "程式下載安裝中..."\n'
		for i in range(total_check_button):
			if check_status[i]:
				bash_to_exe += install_command[i]
				now_bar_pos += 1
				#kde
				
				bash_to_exe += '$prog $dbusRef Set "" value '+str(now_bar_pos)+'\n'
		#zenity 2用這個
		#bash_to_exe += ') | (zenity --progress --width=420 --text="程式下載安裝中，安裝時間會因網路速度而有所差異，敬請稍候" --auto-close) && zenity --info --text 安裝完成 || zenity --info --text 安裝失敗'		
		#zenity 3以上用這個
		#bash_to_exe += ') | (zenity --progress --no-cancel --width=420 --text="程式下載安裝中，安裝時間會因網路速度而有所差異，敬請稍候" --auto-close) && zenity --info --text 安裝完成 || zenity --info --text 安裝失敗\n'
		#kde
		
		bash_to_exe += '$prog $dbusRef close\n'
		
		bash_to_exe += '''
		install_finish_msg=''
		
		if [ "$ure_installed" != -1 ]; then
			if [ "$ure_installed" == 0 ]; then
				install_finish_msg="$install_finish_msg""ubuntu-restricted-extras:安裝成功"$"\\n"
			else
				install_finish_msg="$install_finish_msg""ubuntu-restricted-extras:安裝失敗"$"\\n"
			fi
		fi
		
		
		if [ "$libdvdcss2_installed" != -1 ]; then
			if [ "$libdvdcss2_installed" == 0 ]; then
				install_finish_msg="$install_finish_msg""libdvdcss2:安裝成功"$"\\n"
			else
				install_finish_msg="$install_finish_msg""libdvdcss2:安裝失敗"$"\\n"
			fi
		fi
		
		echo $install_finish_msg > log
		kdialog --msgbox "$install_finish_msg"
		'''
		
		#print bash_to_exe
		f = open(sh_file, 'w')
		f.write(bash_to_exe)
		f.close()
		#os.system('gksu -m 請輸入您的使用者密碼，以便安裝 "gnome-terminal -x /bin/bash '+sh_file+' "')
		os.system('gksu -m 請輸入您的使用者密碼，以便安裝 "konsole -e /bin/bash '+sh_file+' "')
		gtk.main_quit()
	
	def __init__(self, ed):
		global install_command
		self.ed = ed
		
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("安裝多媒體套件")
		self.window.set_border_width(10)
		color = gtk.gdk.color_parse(BG_COLOR)
		#self.window.modify_bg(gtk.STATE_NORMAL, color)
		self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
		box1 = gtk.VBox(False, 0)

		#[top]
		text_show = """歡迎您使用 ezgo11
由於 ezgo11 所預先安裝的程式皆為自由軟體，有些常用的免費軟體
因為授權的關係，所以並沒有預先安裝。
為了讓您在 ezgo11 有更好的體驗，建議安裝下列常用的免費套件："""
		#label = gtk.Label('<span size="'+str(WELCOME_SIZE)+'">歡迎使用 ezgo！強烈建議您應該安裝下列項目：</span>')
		label = gtk.Label('<span size="'+str(WELCOME_SIZE)+'">' +text_show  +'</span>')
		
		label.set_use_markup(True)
		label.show()
		box1.pack_start(label, padding=20)

		separator = gtk.HSeparator()
		separator.show()
		box1.pack_start(separator, padding=5)
		#[app]
		title = "ubuntu-restricted-extras"
		msg = "讓你可以看youtube線上影片及多種影音檔案"
		box2 = newImageBox("ubuntu.png",title,msg,'ubuntu-restricted-extras')
		install_command += ['''echo "install ubuntu-restricted-extras"
			echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
			apt-get install -y --force-yes --quiet ubuntu-restricted-extras >&2
			ure_installed=$?
			''']
		box1.pack_start(box2)

		title = "libdvdcss2"
		msg = "讓你可以看DVD電影"
		box2 = newImageBox("cd-cover.png",title,msg,'libdvdcss2')
		install_command += ['''echo "install libdvdcss2"
			apt-get install -y --force-yes --quiet libdvdcss2 >&2
			libdvdcss2_installed=$?
			''']
		box1.pack_start(box2)

		box1.show()
		self.window.add(box1)

		#[button]
		separator = gtk.HSeparator()
		separator.show()
		box1.pack_start(separator, padding=20)


		#[don't show again button]
		button = gtk.CheckButton("下次不要再自動開啟這個視窗")
		button.connect("clicked", dontshow_button_callback, None)
		box1.pack_start(button, padding=0)

		
		box2 = gtk.HBox()
		#[apply_button]
		button = gtk.Button(stock=gtk.STOCK_APPLY)
		button.connect("clicked", self.apply_press_callback, self)
		box2.pack_end(button,expand=False,padding=10)
		#[cancel_button]
		button = gtk.Button(stock=gtk.STOCK_CANCEL)
		button.connect("destroy", self.destroy_event)
		button.connect_object("clicked", gtk.Widget.destroy, self.window)
		box2.pack_start(button,expand=False,padding=10)
		box1.pack_start(box2, padding=0)

		#[callback]
		self.window.connect("delete_event", self.delete_event)
		self.window.show_all();

class EndMessage:
	def destroy(self, widget, data=None):
		gtk.main_quit()
		
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False
		
	def __init__(self) :
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_title("注意")
		self.window.set_border_width(10)
		color = gtk.gdk.color_parse(BG_COLOR)
		#self.window.modify_bg(gtk.STATE_NORMAL, color)
		self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

		box1 = gtk.VBox(False, 0)
		#box1.set_spacing(gtk.BUTTONBOX_EDGE)

		label = gtk.Label('<span size="'+str(MSG_SIZE)+'"></span>')
		label.set_use_markup(True)
		box1.pack_start(label,expand=False)

		button = gtk.Button(stock=gtk.STOCK_OK)
		button.connect_object("clicked", gtk.Widget.destroy, self.window)
		box1.pack_start(button,expand=False, fill=False)

		self.window.add(box1)
		self.window.connect("destroy", self.destroy)
		self.window.connect("delete_event", self.delete_event)


if __name__ == "__main__":
	#print sys.argv
	force_show = (len(sys.argv)>=2 and sys.argv[1]=='-f')
	
	if (not os.path.exists(dont_show_file)) or force_show :
		os.system('rm -f '+dont_show_file)
		ed = EndMessage()
		fw = FlashInstall(ed)
		if not force_show :
			select_count = check_status.count(True)
			if select_count==0 :
				exit()
		gtk.main()
		#os.system('zenity --info --text 日後若需安裝，請點選"應用程式選單->ezgo工具箱->安裝多媒體套件"')
		os.system('kdialog --msgbox 日後若需安裝，請點選"應用程式選單->ezgo工具箱->安裝多媒體套件"')
