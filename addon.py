﻿# -*- coding: utf-8 -*-
# default.py

import xbmcgui, xbmcaddon, xbmc
import json, sys, urllib, urllib2, gzip, StringIO, re

__addonid__ = "plugin.video.youkutv"
__addon__ = xbmcaddon.Addon(id=__addonid__)
__cwd__ = __addon__.getAddonInfo('path')
__profile__    = xbmc.translatePath( __addon__.getAddonInfo('profile') )
__resource__   = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'lib' ) )
sys.path.append (__resource__)
HOST='http://tv.api.3g.youku.com/'
IDS='pid=0dd34e6431923a46&guid=46a51fe8d8e37731535bade1e6b8ae96&gdid=dab5d487f39cab341ead7b2aa90f9caf&ver=2.3.0'
Navigation=['首页', '频道', '排行']
ContentID=[520, 560, 600]


ACTION_MOVE_LEFT      = 1
ACTION_MOVE_RIGHT     = 2
ACTION_MOVE_UP        = 3
ACTION_MOVE_DOWN      = 4
ACTION_PAGE_UP        = 5
ACTION_PAGE_DOWN      = 6
ACTION_SELECT_ITEM    = 7
ACTION_HIGHLIGHT_ITEM = 8
ACTION_PARENT_DIR_OLD = 9
ACTION_PARENT_DIR     = 92
ACTION_PREVIOUS_MENU  = 10
ACTION_SHOW_INFO      = 11
ACTION_PAUSE          = 12
ACTION_STOP           = 13
ACTION_NEXT_ITEM      = 14
ACTION_PREV_ITEM      = 15
ACTION_SHOW_GUI       = 18
ACTION_PLAYER_PLAY    = 79
ACTION_MOUSE_LEFT_CLICK = 100
ACTION_MOUSE_MOVE     = 107
ACTION_CONTEXT_MENU   = 117


class BaseWindow(xbmcgui.WindowXML):
    def __init__( self, *args, **kwargs):
        self.session = None
        self.oldWindow = None
        xbmcgui.WindowXML.__init__( self )

    def doClose(self):
        self.session.window = self.oldWindow
        self.close()
        
    def onInit(self):
        if self.session:
            self.session.window = self
        else:
            try:
                self.session = VstSession(self)
            except:
                self.close()
        self.setSessionWindow()
        
        
    def onFocus( self, controlId ):
        self.controlId = controlId
        
    def setSessionWindow(self):
        try:
            self.oldWindow = self.session.window
        except:
            self.oldWindow=self
        self.session.window = self
        
    def onAction(self,action):
        if action.getId() == ACTION_PARENT_DIR or action.getId() == ACTION_PREVIOUS_MENU:
            if xbmc.Player().isPlaying():
                xbmc.Player().stop()
            self.doClose()
        else:
            return False

        return True


class HomeWindow(BaseWindow):
    def __init__( self, *args, **kwargs):
        self.inited = False
        BaseWindow.__init__(self, args, kwargs)

    def onInit(self):
        self.initOnce()
        BaseWindow.onInit(self)

    def initOnce(self):
        if self.inited:
            return

        print str(self.inited)

        #Init navigation
        for item in Navigation:
            listitem = xbmcgui.ListItem(label=item)
            self.getControl(510).addItem(listitem)
        
        for Id in ContentID[1:]:
            self.getControl(Id).setVisible(False)

        self.selectedNavigation = 0
        self.getControl(510).getListItem(0).select(True)
        self.setFocusId(510)
            
        self.updateHome()
        self.updateChannelTop()

        self.inited = True
    
    def updateHome(self):
        data = GetHttpData(HOST + 'tv/main?' + IDS)
        data = json.loads(data)
        if not data['status']:
            return
        if data['status'] != 'success':
            return
        for item in data['results']['m1']:
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['image'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(521).addItem(listitem)
            
        for item in data['results']['m2']:
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['big_vertical_image'])
            listitem.setProperty('showid', item['showid'])
            listitem.setProperty('videoid', item['videoid'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(522).addItem(listitem)
            
        item = data['results']['m3'][0]
        listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['big_horizontal_image'])
        listitem.setProperty('showid', item['showid'])
        listitem.setProperty('videoid', item['videoid'])
        listitem.setProperty('mtype', item['mtype'])
        self.getControl(524).addItem(listitem)        
            
        for item in data['results']['m3'][1:]:
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['big_vertical_image'])
            listitem.setProperty('showid', item['showid'])
            listitem.setProperty('videoid', item['videoid'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(525).addItem(listitem)
            
        item = data['results']['m4'][0]
        listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['big_horizontal_image'])
        listitem.setProperty('showid', item['showid'])
        listitem.setProperty('videoid', item['videoid'])
        listitem.setProperty('mtype', item['mtype'])
        self.getControl(527).addItem(listitem)        
            
        for item in data['results']['m4'][1:]:
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['big_vertical_image'])
            listitem.setProperty('showid', item['showid'])
            listitem.setProperty('videoid', item['videoid'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(528).addItem(listitem)
            

    def updateChannelTop(self):
        data = GetHttpData(HOST + 'tv/main/top?' + IDS)
        data = json.loads(data)
        if not data['status']:
            return
        if data['status'] != 'success':
            return

        #Channel
        for i in range(0, len(data['results']['channel']), 2):
            item = data['results']['channel'][i]
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['image'])
            listitem.setProperty('cid', item['cid'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(560).addItem(listitem)

        for i in range(1, len(data['results']['channel']), 2):
            item = data['results']['channel'][i]
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['image'])
            listitem.setProperty('cid', item['cid'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(560).addItem(listitem)

        #Top
        for item in data['results']['top']:
            listitem = xbmcgui.ListItem(label=item['title'], thumbnailImage=item['image'])
            listitem.setProperty('top_id', item['top_id'])
            listitem.setProperty('mtype', item['mtype'])
            self.getControl(600).addItem(listitem)
        

    def onClick( self, controlId ):
        if controlId == 510:
            self.updateNavigation()
        else:
            item = self.getControl(controlId).getSelectedItem()
            if item.getProperty('mtype') == 'show':
                play(item.getProperty('videoid'))
            else:
                xbmcgui.Dialog().ok('提示框', '此功能暂未实现，尽请期待')


    def onAction(self, action):
        BaseWindow.onAction(self, action)
        if action.getId() == ACTION_MOVE_LEFT or action.getId() == ACTION_MOVE_RIGHT or action.getId() == ACTION_MOUSE_MOVE:
            self.updateNavigation()


    def updateNavigation(self):
        if self.getFocusId() == 510:
            if self.selectedNavigation != self.getControl(510).getSelectedPosition():
                #Disable old selection
                self.getControl(510).getListItem(self.selectedNavigation).select(False)
                self.getControl(ContentID[self.selectedNavigation]).setEnabled(False)
                self.getControl(ContentID[self.selectedNavigation]).setVisible(False)

                #Enable new selection
                self.selectedNavigation = self.getControl(510).getSelectedPosition()
                self.getControl(ContentID[self.selectedNavigation]).setEnabled(True)
                self.getControl(ContentID[self.selectedNavigation]).setVisible(True)
                self.getControl(510).getSelectedItem().select(True)



class VstSession:
    def __init__(self,window=None):
        self.window = window
        
    def removeCRLF(self,text):
        return " ".join(text.split())
        
    def makeAscii(self,name):
        return name.encode('ascii','replace')
        
    def closeWindow(self):
        self.window.doClose()
            
    def clearSetting(self,key):
        __addon__.setSetting(key,'')
        
    def setSetting(self,key,value):
        __addon__.setSetting(key,value and ENCODE(value) or '')
        
    def getSetting(self,key,default=None):
        setting = __addon__.getSetting(key)
        if not setting: return default
        if type(default) == type(0):
            return int(float(setting))
        elif isinstance(default,bool):
            return setting == 'true'
        return setting


def play(vid):
    try:
        stypes = ['hd2', 'mp4', 'flv']
        moviesurl="http://v.youku.com/player/getPlayList/VideoIDS/{0}/ctype/12/ev/1".format(vid)
        result = GetHttpData(moviesurl)
        movinfo = json.loads(result.replace('\r\n',''))
        movdat = movinfo['data'][0]
        streamfids = movdat['streamfileids']
        video_id = movdat['videoid']
        stype = 'flv'

        if len(streamfids) > 1:
            selstypes = [v for v in stypes if v in streamfids]
            stype = selstypes[0]
        
        playurl = r'http://v.youku.com/player/getM3U8/vid/' + vid + r'/type/' + stype + '/video.m3u8'
        playlist = xbmc.PlayList(1)
        playlist.clear()
        title =" 第"+str(1)+"/"+str(1)+"节"
        listitem=xbmcgui.ListItem(title)
        listitem.setInfo(type="Video",infoLabels={"Title":title})
        playlist.add(playurl, listitem)
        xbmc.Player().play(playlist)
        return
        
        flvcdurl='http://www.flvcd.com/parse.php?format=super&kw='+urllib.quote_plus(url)
        result = GetHttpData(flvcdurl)
        foobars = re.compile('(http://k.youku.com/.*)"\starget', re.M).findall(result)
        if len(foobars) < 1:
            xbmcgui.Dialog().ok('提示框', '付费视频，无法播放')
            return
        playlist = xbmc.PlayList(1)
        playlist.clear()
        for i in range(0,len(foobars)):
            title =" 第"+str(i+1)+"/"+str(len(foobars))+"节"
            listitem=xbmcgui.ListItem(title)
            listitem.setInfo(type="Video",infoLabels={"Title":title})
            playlist.add(foobars[i], listitem)
        xbmc.Player().play(playlist)
    except:
        xbmcgui.Dialog().ok('提示框', '解析地址异常，无法播放')


def openWindow(window_name,session=None,**kwargs):
    windowFile = '%s.xml' % window_name
    if window_name == 'main':
        w = BaseWindow(windowFile , xbmc.translatePath(__addon__.getAddonInfo('path')), "Default",**kwargs)
    elif window_name == 'home':
        w = HomeWindow(windowFile , xbmc.translatePath(__addon__.getAddonInfo('path')), "Default",session=session,**kwargs)
    else:
        return 
    w.doModal()            
    del w


def GetHttpData(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) {0}{1}'.
                   format('AppleWebKit/537.36 (KHTML, like Gecko) ',
                          'Chrome/28.0.1500.71 Safari/537.36'))
    req.add_header('Accept-encoding', 'gzip')
    response = urllib2.urlopen(req)
    httpdata = response.read()
    if response.headers.get('content-encoding', None) == 'gzip':
        httpdata = gzip.GzipFile(fileobj=StringIO.StringIO(httpdata)).read()
    response.close()
    match = re.compile('encodingt=(.+?)"').findall(httpdata)
    if len(match)<=0:
        match = re.compile('meta charset="(.+?)"').findall(httpdata)
    if len(match)>0:
        charset = match[0].lower()
        if (charset != 'utf-8') and (charset != 'utf8'):
            httpdata = unicode(httpdata, charset).encode('utf8')
    return httpdata


if __name__ == '__main__':
    openWindow('home')
