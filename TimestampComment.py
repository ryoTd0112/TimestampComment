import sys
from datetime import datetime, timedelta
from json import dumps, load
from os import mkdir, name
from os.path import dirname, exists, join
from unicodedata import east_asian_width
from webbrowser import open as webopen

from wx import (ALIGN_CENTER, ALIGN_TOP, ALL, ALWAYS_SHOW_SB, BOTTOM,
                EVT_BUTTON, EVT_MENU, EVT_TEXT, EVT_TIMER, EXPAND, FD_SAVE,
                FIXED_MINSIZE, FONTFAMILY_DEFAULT, FONTFAMILY_MODERN,
                FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL, HORIZONTAL, HSCROLL,
                ID_ANY, ID_OK, LEFT, RIGHT, TAB_TRAVERSAL, TE_MULTILINE,
                TE_PROCESS_ENTER, TE_READONLY, TOP, VERTICAL, App, BoxSizer,
                Button, DefaultPosition, DefaultSize, Dialog, FileDialog,
                FlexGridSizer, Font, Frame, GridSizer, Icon, Menu, MenuBar,
                NewIdRef, Panel, StaticLine, StaticText, TextCtrl, Timer)
from wx.lib.scrolledpanel import ScrolledPanel

LANGUAGE_FILE = 'Language file'
WELCOME_FILE = 'Welcome file'
ABOUT_FILE = 'About file'
ICON_FILE = 'Icon file'

TEXT_SEPARETER = r'{ENDOFONELANGUAGE}'

DEFAULT_LANGUAGE = 'Default language'
SPACE_LENGTH_LABEL = 'Space length label'
WRAP_LENGTH_LABEL = 'Wrap length label'
NEWLINE_COUNT_LABEL = 'Newline count label'

DEFAULT_SETTING_FILE_PATH = 'configure/DefaultSetting.json'
DEFAULT_SETTING = {
    LANGUAGE_FILE: "configure/Language.json",
    WELCOME_FILE: "configure/Welcome.txt",
    ABOUT_FILE: "configure/About.txt",
    ICON_FILE: "icon.ico",
    DEFAULT_LANGUAGE: 0,
    SPACE_LENGTH_LABEL: 2,
    WRAP_LENGTH_LABEL: 43,
    NEWLINE_COUNT_LABEL: 4
}
DEFAULT_LANGUAGE_FILE = [
    {
        "Title": "Time Stamp Comment",
        "Language": "Language",
        "Language Setting": "English",

        "File": "File",
        "Export": "Export\tCtrl+O",
        "Exit": "Exit\tCtrl+E",

        "Edit": "Edit",
        "Timer": "Timer",
        "Start": "Start\tCtrl+S",
        "Pause": "Pause\tCtrl+P",
        "Reset": "Reset\tCtrl+R",
        "Time Stamp": "Time Stamp",
        "New": "New\tCtrl+N",

        "View": "View",
        "Show Preview": "Show Preview\tCtrl+Shift+P",

        "Help": "Help",
        "Welcome": "Welcome\tCtrl+Shift+H",
        "Visit Github": "Visit Github",
        "About": "About",

        "Space length label": "Space Length",
        "Wrap length label": "Wrap Length",
        "Newline count label": "Newline Count",

        "Save As...": "Save As..."
    },
    {
        "Title": "タイムスタンプ コメント",
        "Language": "言語",
        "Language Setting": "日本語",

        "File": "ファイル",
        "Export": "出力\tCtrl+O",
        "Exit": "閉じる\tCtrl+E",

        "Edit": "編集",
        "Timer": "タイマー",
        "Start": "開始\tCtrl+S",
        "Pause": "一時停止\tCtrl+P",
        "Reset": "停止\tCtrl+R",
        "Time Stamp": "タイムスタンプ",
        "New": "新規\tCtrl+N",
        "Write": "入力\tCtrl+W",
        "Delete": "削除\tCtrl+D",

        "View": "表示",
        "Show Preview": "プレビューを見る\tCtrl+Shift+P",

        "Help": "ヘルプ",
        "Welcome": "ようこそ\tCtrl+Shift+H",
        "Visit Github": "Githubを開く",
        "Visit Twitter": "Twitterで開く",
        "About": "このアプリについて",

        "Space length": "スペース",
        "Wrap length": "折り返し",
        "Newline count": "行間隔",

        "Save As...": "保存先..."
    }
]
ERROR_MESSAGE = 'Check the location of the configuration file.'

NORMAL = NewIdRef()
RUNNING = NewIdRef()
PAUSE = NewIdRef()
ERROR = NewIdRef()

SHOW_LABEL = '↑'
HIDE_LABEL = '↓'
START_LABEL = '▶'
PAUSE_LABEL = '||'
STOP_LABEL = '■'
ADD_LABEL = '+'
TIMER_LABEL = '00:00:00'

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480

ID_FILE = 0
ID_FILE_EXPORT = NewIdRef()
ID_FILE_EXIT = NewIdRef()

ID_EDIT = 1
ID_EDIT_TIMER_START = NewIdRef()
ID_EDIT_TIMER_PAUSE = NewIdRef()
ID_EDIT_TIMER_RESTART = NewIdRef()
ID_EDIT_TIMER_RESET = NewIdRef()
ID_EDIT_TIME_STAMP_NEW = NewIdRef()
ID_EDIT_TIME_STAMP_WRITE = NewIdRef()
ID_EDIT_TIME_STAMP_DELETE = NewIdRef()

ID_VIEW = 2
ID_VIEW_SHOW_PREVIEW = NewIdRef()

ID_HELP = 3
ID_HELP_WELCOME = NewIdRef()
ID_HELP_VISIT_GITHUB = NewIdRef()
ID_HELP_VISIT_TWITTER = NewIdRef()
ID_HELP_ABOUT = NewIdRef()


class SettingManeger(object):
    def __init__(self):
        super().__init__()
        self.default_setting_file = find_data_file(DEFAULT_SETTING_FILE_PATH)

        self.setting = open_json_file(self.default_setting_file)
        if self.setting is None:
            self.setting = DEFAULT_SETTING

        language_file = get_data_safety(self.setting, LANGUAGE_FILE)
        self.language_list = open_json_file(find_data_file(language_file))
        if self.language_list is None:
            self.language_list = DEFAULT_LANGUAGE_FILE

        self.language_index = get_data_safety(self.setting, DEFAULT_LANGUAGE, 0)
        self.language_index = min(self.language_index, len(self.language_list))

        welcome_file = get_data_safety(self.setting, WELCOME_FILE)
        welcome_contents = open_txt_file(welcome_file)
        self.welcome_contents_list = welcome_contents.split(TEXT_SEPARETER) if welcome_contents is not None else None

        about_file = get_data_safety(self.setting, ABOUT_FILE)
        about_contents = open_txt_file(about_file)
        self.about_contents_list = open_txt_file(about_file).split(TEXT_SEPARETER) if about_contents is not None else None

        self.space_length = get_data_safety(self.setting, SPACE_LENGTH_LABEL, 2)
        self.wrap_length = get_data_safety(self.setting, WRAP_LENGTH_LABEL, 43)
        self.newline_count = get_data_safety(self.setting, NEWLINE_COUNT_LABEL, 4)

    def save_setting(self):
        self.setting[DEFAULT_LANGUAGE] = self.language_index
        self.setting[SPACE_LENGTH_LABEL] = self.space_length
        self.setting[WRAP_LENGTH_LABEL] = self.wrap_length
        self.setting[NEWLINE_COUNT_LABEL] = self.newline_count
        setting_json = dumps(self.setting)

        configure_path = find_data_file('configure')
        if not exists(configure_path):
            mkdir(configure_path)
        with open(self.default_setting_file, mode='w') as f:
            f.write(setting_json)

    def set_parameter(self, value):
        self.space_length, self.wrap_length, self.newline_count = value

    @property
    def selected_language(self):
        return None if None is self.language_list else self.language_list[self.language_index]

    @property
    def formmat_parameter(self):
        return self.space_length, self.wrap_length, self.newline_count


class MainWindow(Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.sm = SettingManeger()

        icon_file = get_data_safety(self.sm.setting, ICON_FILE)
        if icon_file is not None and exists(icon_file):
            icon = Icon(find_data_file(icon_file))
            self.SetIcon(icon)
        self.menubar, self.language_menu_item_list = self.create_menubar(self.sm.language_list)
        self.SetMenuBar(self.menubar)

        if 0 <= len(self.language_menu_item_list) - 1 <= self.sm.language_index:
            self.language_menu_item_list[self.sm.language_index].Check()

        self.panel = Panel(self)
        self.preview_button = NormalButton(self.panel, label=SHOW_LABEL, size=(40, 40), pos=(10, 10))
        self.separeter_line = StaticLine(self.panel, size=(3000, 2))
        self.add_button = NormalButton(self.panel, label=ADD_LABEL, size=(40, 40))

        self.timer_display = TimerDisplay(self, parent=self.panel)
        self.contents_display = ContentsDisplay(self, self.timer_display, parent=self.panel, style=ALWAYS_SHOW_SB)

        self.preview_window = PreviewWindow(self.sm, self.contents_display, parent=self)
        welcome_contents = self.sm.welcome_contents_list[self.sm.language_index] if self.sm.welcome_contents_list is not None else ERROR_MESSAGE
        self.welcome_window = ScrolledWindow(welcome_contents, parent=self)
        about_contents = self.sm.about_contents_list[self.sm.language_index] if self.sm.about_contents_list is not None else ERROR_MESSAGE
        self.about_window = ScrolledWindow(about_contents, parent=self)

        self.reset()

        self.change_language()
        self.connect()
        self.set_color()
        self.layout()

    def connect(self):
        self.menubar.Bind(EVT_MENU, lambda x: self.contents_display.export(), id=ID_FILE_EXPORT)
        self.menubar.Bind(EVT_MENU, lambda x: self.Destroy(), id=ID_FILE_EXIT)
        self.menubar.Bind(EVT_MENU, lambda x: self.run(), id=ID_EDIT_TIMER_START)
        self.menubar.Bind(EVT_MENU, lambda x: self.pause(), id=ID_EDIT_TIMER_PAUSE)
        self.menubar.Bind(EVT_MENU, lambda x: self.reset(), id=ID_EDIT_TIMER_RESET)
        self.menubar.Bind(EVT_MENU, lambda x: self.new(), id=ID_EDIT_TIME_STAMP_NEW)
        self.menubar.Bind(EVT_MENU, lambda x: self.show_preview(), id=ID_VIEW_SHOW_PREVIEW)
        self.menubar.Bind(EVT_MENU, lambda x: self.welcome_window.Show(), id=ID_HELP_WELCOME)
        self.menubar.Bind(EVT_MENU, lambda x: open_github(), id=ID_HELP_VISIT_GITHUB)
        self.menubar.Bind(EVT_MENU, lambda x: self.about_window.Show(), id=ID_HELP_ABOUT)

        self.timer_display.start_btn.Bind(EVT_BUTTON, lambda x: self.run())
        self.timer_display.pause_btn.Bind(EVT_BUTTON, lambda x: self.pause())
        self.timer_display.reset_btn.Bind(EVT_BUTTON, lambda x: self.reset())
        self.preview_button.Bind(EVT_BUTTON, lambda x: self.show_preview())
        self.add_button.Bind(EVT_BUTTON, lambda x: self.new())

    def set_color(self):
        pass

    def layout(self):
        vbox = BoxSizer(VERTICAL)

        vbox.Add(self.timer_display, 0, EXPAND)
        vbox.Add(self.contents_display, 1, EXPAND | LEFT, 10)
        vbox.Add(self.separeter_line, 0, TOP, 5)
        vbox.Add(self.add_button, 0, ALIGN_CENTER | TOP | BOTTOM, 5)
        self.panel.SetSizer(vbox)
        self.Show()

    def create_menubar(self, language_list, style=0):
        modifier = 'Ctrl' if name == 'nt' else 'Opt'
        menubar = MenuBar()
        menubar_file = Menu()
        menubar_file.Append(ID_FILE_EXPORT, '&Export\t' + modifier + 'E')
        menubar_file.AppendSeparator()
        menubar_file.Append(ID_FILE_EXIT, 'E&xit\t' + modifier + 'W')

        menubar_edit = Menu()
        menubar_edit_timer = Menu()
        menubar_edit.AppendSubMenu(menubar_edit_timer, '&Timer')
        menubar_edit_timer.Append(ID_EDIT_TIMER_START, '&Start\t' + modifier + 'S')
        menubar_edit_timer.Append(ID_EDIT_TIMER_PAUSE, '&Pause\t' + modifier + 'P')
        menubar_edit_timer.Append(ID_EDIT_TIMER_RESET, '&Reset\t' + modifier + 'R')
        menubar_edit_time_stamp = Menu()
        menubar_edit.AppendSubMenu(menubar_edit_time_stamp, 'Time &Stamp')
        menubar_edit_time_stamp.Append(ID_EDIT_TIME_STAMP_NEW, '&New\t' + modifier + 'N')

        menubar_view = Menu()
        menubar_view.AppendCheckItem(ID_VIEW_SHOW_PREVIEW, 'Show &Preview\t' + modifier + 'Shift+P')
        menubar_view_language = Menu()

        language_menu_item_list = []
        if language_list is not None:
            menubar_view_language.Bind(EVT_MENU, lambda x: self.change_language())
            menubar_view.AppendSubMenu(menubar_view_language, '&Language')

            for n in range(len(language_list)):
                language_menu_item_list.append(menubar_view_language.AppendRadioItem(ID_ANY, language_list[n]['Language Setting']))

        menubar_help = Menu()
        menubar_help.Append(ID_HELP_WELCOME, '&Welcome\t' + modifier + 'Shift+H')
        menubar_help.AppendSeparator()
        menubar_help.Append(ID_HELP_VISIT_GITHUB, 'Visit &Github')
        menubar_help.AppendSeparator()
        menubar_help.Append(ID_HELP_ABOUT, '&About')

        menubar.Append(menubar_file, '&File')
        menubar.Append(menubar_edit, '&Edit')
        menubar.Append(menubar_view, '&View')
        menubar.Append(menubar_help, '&Help')

        return menubar, language_menu_item_list

    def change_language(self):
        modifier = 'Ctrl' if name == 'nt' else 'Opt'
        self.sm.language_index = self.selected_language
        selected_language = self.sm.selected_language

        file_ = get_data_safety(selected_language, 'File', '&File')
        export = get_data_safety(selected_language, 'Export', '&Export\t' + modifier + 'E')
        exit_ = get_data_safety(selected_language, 'Exit', 'E&xit\t' + modifier + 'W')
        self.menubar.SetMenuLabel(ID_FILE, file_)
        self.menubar.FindItemById(ID_FILE_EXPORT).SetItemLabel(export)
        self.menubar.FindItemById(ID_FILE_EXIT).SetItemLabel(exit_)

        edit = get_data_safety(selected_language, 'Edit', '&Edit')
        timer = get_data_safety(selected_language, 'Timer', '&Timer')
        start = get_data_safety(selected_language, 'Start', '&Start\t' + modifier + 'S')
        pause = get_data_safety(selected_language, 'Pause', '&Pause\t' + modifier + 'P')
        reset = get_data_safety(selected_language, 'Reset', '&Reset\t' + modifier + 'R')
        time_stamp = get_data_safety(selected_language, 'Time Stamp', 'Time &Stamp')
        new = get_data_safety(selected_language, 'New', '&New\t' + modifier + 'N')
        self.menubar.SetMenuLabel(ID_EDIT, edit)
        self.menubar.GetMenu(ID_EDIT).FindItemByPosition(0).SetItemLabel(timer)
        self.menubar.FindItemById(ID_EDIT_TIMER_START).SetItemLabel(start)
        self.menubar.FindItemById(ID_EDIT_TIMER_PAUSE).SetItemLabel(pause)
        self.menubar.FindItemById(ID_EDIT_TIMER_RESET).SetItemLabel(reset)
        self.menubar.GetMenu(ID_EDIT).FindItemByPosition(1).SetItemLabel(time_stamp)
        self.menubar.FindItemById(ID_EDIT_TIME_STAMP_NEW).SetItemLabel(new)

        view = get_data_safety(selected_language, 'View', '&View')
        show_preview = get_data_safety(selected_language, 'Show Preview', 'Show &Preview\t' + modifier + 'Shift+P')
        language = get_data_safety(selected_language, 'Language', '&Language')
        self.menubar.SetMenuLabel(ID_VIEW, view)
        self.menubar.FindItemById(ID_VIEW_SHOW_PREVIEW).SetItemLabel(show_preview)
        self.menubar.GetMenu(ID_VIEW).FindItemByPosition(1).SetItemLabel(language)

        help_ = get_data_safety(selected_language, 'Help', '&Help')
        welcome = get_data_safety(selected_language, 'Welcome', '&Welcome\t' + modifier + 'Shift+H')
        visit_github = get_data_safety(selected_language, 'Visit Github', 'Visit &Github')
        about = get_data_safety(selected_language, 'About', '&About')
        self.menubar.SetMenuLabel(ID_HELP, help_)
        self.menubar.FindItemById(ID_HELP_WELCOME).SetItemLabel(welcome)
        self.menubar.FindItemById(ID_HELP_VISIT_GITHUB).SetItemLabel(visit_github)
        self.menubar.FindItemById(ID_HELP_ABOUT).SetItemLabel(about)

        shown_welcome_window = self.welcome_window.IsShown()
        self.welcome_window.Destroy(True)
        welcome_content = self.sm.welcome_contents_list[self.selected_language] if self.sm.welcome_contents_list is not None else ERROR_MESSAGE
        self.welcome_window = ScrolledWindow(welcome_content, parent=self)
        self.welcome_window.Show(shown_welcome_window)

        shown_about_window = self.about_window.IsShown()
        self.about_window.Destroy(True)
        about_content = self.sm.about_contents_list[self.selected_language] if self.sm.about_contents_list is not None else ERROR_MESSAGE
        self.about_window = ScrolledWindow(about_content, parent=self)
        self.about_window.Show(shown_about_window)

        shown_preview_window = self.preview_window.IsShown()
        self.preview_window.Destroy(True)
        self.preview_window = PreviewWindow(self.sm, self.contents_display, parent=self)
        self.preview_window.Show(shown_preview_window)

    def run(self):
        self.add_button.Enable()
        self.preview_button.Enable()
        self.menubar.FindItemById(ID_FILE_EXPORT).Enable(True)
        self.menubar.FindItemById(ID_EDIT_TIMER_START).Enable(False)
        self.menubar.FindItemById(ID_EDIT_TIMER_PAUSE).Enable(True)
        self.menubar.FindItemById(ID_EDIT_TIMER_RESET).Enable(True)
        self.menubar.FindItemById(ID_EDIT_TIME_STAMP_NEW).Enable(True)
        self.menubar.FindItemById(ID_VIEW_SHOW_PREVIEW).Enable(True)
        self.timer_display.start()

    def pause(self):
        self.menubar.FindItemById(ID_EDIT_TIMER_START).Enable(True)
        self.menubar.FindItemById(ID_EDIT_TIMER_PAUSE).Enable(False)
        self.menubar.FindItemById(ID_EDIT_TIMER_RESET).Enable(True)

        self.timer_display.pause()

    def reset(self):
        self.menubar.FindItemById(ID_FILE_EXPORT).Enable(False)
        self.menubar.FindItemById(ID_EDIT_TIMER_START).Enable(True)
        self.menubar.FindItemById(ID_EDIT_TIMER_PAUSE).Enable(False)
        self.menubar.FindItemById(ID_EDIT_TIMER_RESET).Enable(False)
        self.menubar.FindItemById(ID_EDIT_TIME_STAMP_NEW).Enable(False)
        self.menubar.FindItemById(ID_VIEW_SHOW_PREVIEW).Enable(False)
        if self.preview_window.IsShown():
            self.show_preview()

        self.add_button.Disable()
        self.preview_button.Disable()

        self.timer_display.reset()
        self.contents_display.reset()

    def new(self):
        self.contents_display.add_contents_panel()
        self.preview_window.update()

    def show_preview(self):
        menu_show_preview = self.menubar.FindItemById(ID_VIEW_SHOW_PREVIEW)
        if self.preview_window.IsShown():
            self.preview_button.SetLabel(SHOW_LABEL)
            menu_show_preview.Check(False)
            self.preview_window.Hide()
        else:
            self.preview_button.SetLabel(HIDE_LABEL)
            menu_show_preview.Check(True)
            self.preview_window.update()
            self.preview_window.Show()

    def Destroy(self):
        self.sm.save_setting()
        return super().Destroy()

    @property
    def selected_language(self):
        for n, menu_item in enumerate(self.language_menu_item_list):
            if menu_item.IsChecked():
                return n


class ScrolledWindow(Frame):
    def __init__(self, contents, *args, **kw):
        super().__init__(*args, **kw)
        icon_bundle = self.GetParent().GetIcons()
        if not icon_bundle.IsEmpty():
            self.SetIcon(icon_bundle.GetIconByIndex(0))

        self.scrolled_panel = ScrolledPanel(self)
        self.contents = HelpText(self.scrolled_panel, style=TE_MULTILINE)
        self.layout()
        self.contents.SetLabel(contents)
        self.SetupScrolling()

    def layout(self):
        self.vbox = BoxSizer(VERTICAL)
        self.vbox.Add(self.contents, 0, ALL, 25)
        self.scrolled_panel.SetSizer(self.vbox)

    def Fit(self):
        self.scrolled_panel.Fit()
        return super().Fit()

    def SetupScrolling(self):
        self.Fit()
        width, height = self.GetSize()
        height = min(height, WINDOW_HEIGHT)
        self.SetSize(0, 0, width, height)

        self.scrolled_panel.SetupScrolling()

    def Show(self, show=True):
        if self.IsShown() and show:
            self.Raise()
        self.Center()
        return super().Show(show=show)

    def Destroy(self, is_destroy=False):
        self.Hide()
        return is_destroy


class TimerDisplay(Panel):
    def __init__(self, main_window, *args, **kw):
        super().__init__(*args, **kw)
        self.timer = Timer(self)

        self.main_window = main_window

        self.time_display = WatchText(self, label=TIMER_LABEL)
        self.start_btn = NormalButton(self, label=START_LABEL)
        self.pause_btn = NormalButton(self, label=PAUSE_LABEL)
        self.reset_btn = NormalButton(self, label=STOP_LABEL)

        self.maneger = TimeManeger(self.main_window, self)
        self.layout()
        self.Bind(EVT_TIMER, self.update_watch)

    def layout(self):
        vbox = BoxSizer(VERTICAL)
        self.SetSizer(vbox)
        hbox = BoxSizer(HORIZONTAL)

        hbox.Add(self.start_btn, 1, ALIGN_CENTER | RIGHT, 10)
        hbox.Add(self.pause_btn, 1, ALIGN_CENTER | RIGHT | LEFT, 5)
        hbox.Add(self.reset_btn, 1, ALIGN_CENTER | LEFT, 10)

        vbox.Add(self.time_display, 0, ALIGN_CENTER | ALL, 10)
        vbox.Add(hbox, 1, ALIGN_CENTER)
        vbox.Add(StaticLine(self, ID_ANY, size=(3000, 2)), 0, TOP, 5)

        self.pause_btn.Disable()
        self.reset_btn.Disable()

    def start(self):
        if self.state not in [NORMAL, PAUSE]:
            return

        if self.state == NORMAL:
            self.start_btn.Disable()
            self.pause_btn.Enable()
            self.reset_btn.Enable()

            self.timer.Start(100)
            self.maneger.start()

        elif self.state == PAUSE:
            self.restart()

    def pause(self):
        self.start_btn.Enable()
        self.pause_btn.Disable()
        self.timer.Stop()

        self.maneger.pause()

    def restart(self):
        self.start_btn.Disable()
        self.pause_btn.Enable()
        self.timer.Start()

    def reset(self):
        self.start_btn.Enable()
        self.pause_btn.Disable()
        self.reset_btn.Disable()

        self.time_display.SetLabel(TIMER_LABEL)
        self.timer.Stop()

        self.maneger.reset()

    def update_watch(self, event):
        total_seconds = self.maneger.get_elapsed_time().seconds
        h, m, s = map(str, get_hms(total_seconds))
        watch_label = '{}:{}:{}'.format(h.zfill(2), m.zfill(2), s.zfill(2))
        self.time_display.SetLabel(watch_label)

        event.Skip()

    @property
    def state(self):
        if self.start_btn.IsEnabled() and not self.pause_btn.IsEnabled() and not self.reset_btn.IsEnabled():
            return NORMAL

        if not self.start_btn.IsEnabled() and self.pause_btn.IsEnabled() and self.reset_btn.IsEnabled():
            return RUNNING

        if self.start_btn.IsEnabled() and not self.pause_btn.IsEnabled() and self.reset_btn.IsEnabled():
            return PAUSE

        return ERROR


class TimeManeger(object):
    def __init__(self, main_window, timer_display):
        super().__init__()
        self.main_window = main_window
        self.timer_display = timer_display

        self.start_time = None
        self.pause_time = None
        self.pause_start_time = None

    def get_elapsed_time(self) -> datetime:
        if self.state not in [RUNNING, PAUSE]:
            return

        elapsed_time = datetime.now() - self.start_time - self.pause_time
        if self.state == PAUSE:
            elapsed_time -= datetime.now() - self.pause_start_time
        return elapsed_time

    def start(self):
        if self.state not in [NORMAL, PAUSE]:
            return

        if self.state == NORMAL:
            self.start_time = datetime.now()
            self.pause_time = timedelta(seconds=0)

        elif self.state == PAUSE:
            self.restart()

    def pause(self):
        if self.state != RUNNING:
            return

        self.pause_start_time = datetime.now()

    def restart(self):
        if self.state != PAUSE:
            return

        self.pause_time += datetime.now() - self.pause_start_time
        self.pause_start_time = None

    def reset(self):
        self.start_time = None
        self.pause_time = None
        self.pause_start_time = None

    @property
    def state(self):
        if self.pause_start_time is None and None not in (self.start_time, self.pause_time):
            return RUNNING

        if None not in [self.start_time, self.pause_time, self.pause_start_time]:
            return PAUSE

        if all(x is None for x in [self.start_time, self.pause_time, self.pause_start_time]):
            return NORMAL

        return ERROR


class Contents(object):
    def __init__(self, time: timedelta, caption=''):
        super().__init__()

        self.time = time
        self.caption = caption


class ContentsDisplay(ScrolledPanel):
    def __init__(self, main_window, timer_display, parent, id=-1, pos=DefaultPosition, size=DefaultSize, style=TAB_TRAVERSAL, name='scrolledpanel'):
        super().__init__(parent, id=id, pos=pos, size=size, style=style, name=name)
        self.main_window = main_window
        self.timer_display = timer_display
        self.contents_panel_list = []

        self.layout()

    def layout(self):
        self.SetupScrolling(scroll_x=False)
        self.vbox = BoxSizer(VERTICAL)
        self.SetSizer(self.vbox)

    def add_contents_panel(self):
        time = self.timer_display.maneger.get_elapsed_time()
        contents = Contents(time, '')
        contents_panel = ContentsPanel(contents, parent=self, size=(WINDOW_WIDTH - 40, 100))
        self.contents_panel_list.append(contents_panel)
        self.vbox.Add(contents_panel, 1, EXPAND | FIXED_MINSIZE)
        self.SetupScrolling(scrollToTop=False)
        self.ScrollChildIntoView(contents_panel)
        self.Layout()
        self.Refresh()

    def remove_contents_panel(self, contents_panel):
        index = self.contents_panel_list.index(contents_panel)
        self.contents_panel_list.remove(contents_panel)
        self.vbox.Hide(contents_panel)
        self.vbox.Remove(index)
        self.SetupScrolling(scrollToTop=False)
        self.Layout()
        self.Refresh()

        self.main_window.preview_window.update()

    def reset(self):
        for contents in self.contents_panel_list:
            contents.Hide()
        self.vbox.Clear()
        self.contents_panel_list = []
        self.SetupScrolling(scrollToTop=False)

    def convert_string(self, space_length, wrap_length, newline_count):
        ret = ''

        for contents_panel in self.contents_panel_list:
            contents = contents_panel.contents
            total_seconds = contents.time.seconds
            h, m, s = map(str, get_hms(total_seconds))
            time_formatted = '{}:{}:{}'.format(h.zfill(2), m.zfill(2), s.zfill(2))

            indent_length = self.__count_east_asian_width(time_formatted) + space_length
            cap = contents.caption
            line = time_formatted + ' ' * space_length + cap

            ret += self.__text_wrap(line, indent_length, wrap_length) + '\n' * (newline_count + 1)

        return ret

    def __text_wrap(self, s, indent_length=0, wrap_length=80):

        indent = ' ' * indent_length
        count = 0
        for n, c in enumerate(s):
            count += self.__count_east_asian_width(c)

            if count > wrap_length:
                return s[: n] + '\n' + self.__text_wrap(indent + s[n:], indent_length, wrap_length)
            if c == '\n':
                return s[: n + 1] + self.__text_wrap(indent + s[n + 1:], indent_length, wrap_length)
              
        return s

    def __count_east_asian_width(self, s):
        return sum(2 if east_asian_width(c) in 'FWA' else 1 for c in s)

    def export(self):
        sm = self.main_window.sm
        message = get_data_safety(sm.language, 'Save As...', 'Save As...')
        file_path = choose_file(self.main_window, message)
        if file_path is None:
            return

        space_length, wrap_length, newline_count = sm.formmat_parameter

        with open(file_path, mode='x') as f:
            f.write(self.convert_string(space_length, wrap_length, newline_count))


class ContentsPanel(Panel):
    def __init__(self, contents, *args, **kw):
        super().__init__(*args, **kw)

        self.contents = contents
        self.contents_display = self.GetParent()

        total_seconds = self.contents.time.seconds
        h, m, s = map(str, get_hms(total_seconds))
        time_lbl = '{}:{}:{}'.format(h.zfill(2), m.zfill(2), s.zfill(2))

        self.time = NormalText(self, label=time_lbl)
        self.caption = NormalCaption(self, style=TE_MULTILINE | TE_PROCESS_ENTER)
        self.caption.SetFocus()
        self.delete_button = NormalButton(self, label='X', size=(30, 30))
        self.under_line = StaticLine(self, ID_ANY, size=(3000, 2))

        self.connect()
        self.set_color()
        self.layout()

    def connect(self):
        self.caption.Bind(EVT_TEXT, self.update)
        self.delete_button.Bind(EVT_BUTTON, lambda x: self.contents_display.remove_contents_panel(self))

    def layout(self):
        vbox = BoxSizer(VERTICAL)
        self.SetSizer(vbox)

        hbox = BoxSizer(HORIZONTAL)
        hbox.Add(self.time, 0, ALIGN_TOP | ALL, 5)
        hbox.Add(self.caption, 1, EXPAND | ALL | FIXED_MINSIZE, 5)
        hbox.Add(self.delete_button, 0, ALIGN_TOP | TOP | RIGHT, 5)

        vbox.Add(hbox, 1, EXPAND)
        vbox.Add(self.under_line, 0, ALL | ALIGN_CENTER, 3)

    def set_color(self):
        self.delete_button.SetForegroundColour('#FFF')
        self.delete_button.SetBackgroundColour('#F00')

    def set_focus_setting(self):
        self.delete_button.DisableFocusFromKeyboard()

    def update(self, event):
        self.contents.caption = self.caption.GetValue()
        event.Skip()


class PreviewWindow(Frame):
    def __init__(self, setting_maneger: SettingManeger, contents_display: ContentsDisplay, *args, **kw):
        super().__init__(*args, **kw)
        icon_bundle = self.GetParent().GetIcons()
        if not icon_bundle.IsEmpty():
            self.SetIcon(icon_bundle.GetIconByIndex(0))

        self.sm = setting_maneger
        self.main_window = self.GetParent()
        self.contents_display = contents_display

        self.panel = Panel(self)

        space_length, wrap_length, newline_count = self.sm.formmat_parameter
        self.space_lbl = NormalText(self.panel)
        self.space_display = IncrementWidget(space_length, min_=0, parent=self.panel, listener=self.check)

        self.wrap_lbl = NormalText(self.panel)
        self.wrap_length_display = IncrementWidget(wrap_length, parent=self.panel, listener=self.check)

        self.newline_lbl = NormalText(self.panel)
        self.newline_display = IncrementWidget(newline_count, min_=0, parent=self.panel, listener=self.check)

        self.entry = PreviewEntry(self.panel, style=TE_MULTILINE | TE_READONLY | HSCROLL)

        self.change_language()
        self.set_color()
        self.layout()
        self.update()

        self.contents_display.Bind(EVT_TEXT, self.update)

    def layout(self):
        master_grid = FlexGridSizer(rows=2, cols=1, gap=(0, 0))
        grid = GridSizer(rows=2, cols=3, gap=(0, 0))
        grid.Add(self.space_lbl, 0, ALIGN_CENTER)
        grid.Add(self.wrap_lbl, 0, ALIGN_CENTER)
        grid.Add(self.newline_lbl, 0, ALIGN_CENTER)
        grid.Add(self.space_display, 0, ALIGN_CENTER)
        grid.Add(self.wrap_length_display, 0, ALIGN_CENTER)
        grid.Add(self.newline_display, 0, ALIGN_CENTER)
        master_grid.Add(grid, 0, ALIGN_CENTER | ALL, 10)
        master_grid.Add(self.entry, 1, EXPAND)
        master_grid.AddGrowableRow(1)
        master_grid.AddGrowableCol(0)
        self.panel.SetSizer(master_grid)
        self.panel.Fit()
        self.Fit()
        width, height = self.GetSize()
        height = WINDOW_HEIGHT
        self.SetSize(-1, -1, width, height)

    def set_color(self):
        self.entry.SetBackgroundColour('#eee')

    def change_language(self):
        language = self.sm.selected_language
        space_length_lbl = language[SPACE_LENGTH_LABEL]
        wrap_length_lbl = language[WRAP_LENGTH_LABEL]
        newline_count_lbl = language[NEWLINE_COUNT_LABEL]

        self.space_lbl.SetLabel(space_length_lbl)
        self.wrap_lbl.SetLabel(wrap_length_lbl)
        self.newline_lbl.SetLabel(newline_count_lbl)

        self.panel.Layout()
        self.Layout()

    def check(self):
        space = self.space_display.value
        max_len = self.wrap_length_display.value
        margin = 2
        indent = 8 + space
        if max_len - indent < margin:
            max_len = indent + margin
            self.wrap_length_display.set_value(max_len)

        if indent + margin == max_len:
            self.wrap_length_display.left_btn.Disable()
        else:
            self.wrap_length_display.left_btn.Enable()

        self.panel.Layout()
        self.sm.set_parameter([self.space_display.value, self.wrap_length_display.value, self.newline_display.value])
        self.update()

    def update(self, event=None):
        space_length, wrap_length, newline_count = self.sm.formmat_parameter
        output = self.contents_display.convert_string(space_length, wrap_length, newline_count)
        self.entry.SetValue(output)

        if event is not None:
            event.Skip()

    def Destroy(self, is_destroy=False):
        self.Hide()
        return False


class IncrementWidget(Panel):
    def __init__(self, value=0, min_=None, max_=None, listener=None, *args, **kw):
        super().__init__(*args, **kw)
        self.value = value
        self.min = min_
        self.max = max_
        self.listener = listener

        self.left_btn = NormalButton(parent=self, label='◀', size=(30, 30))
        self.display = NormalText(parent=self, label=str(self.value))
        self.right_btn = NormalButton(parent=self, label='▶', size=(30, 30))

        self.timer = Timer()

        if self.min is not None and self.value <= self.min:
            self.left_btn.Disable()

        if self.max is not None and self.value >= self.max:
            self.right_btn.Disable()

        self.layout()
        self.connect()

    def connect(self):
        self.left_btn.Bind(EVT_BUTTON, self.decrease)
        self.right_btn.Bind(EVT_BUTTON, self.increase)

    def layout(self):
        hbox = BoxSizer(HORIZONTAL)
        hbox.Add(self.left_btn, 0, ALIGN_CENTER | RIGHT, 10)
        hbox.Add(self.display, 1, EXPAND | LEFT | RIGHT, 10)
        hbox.Add(self.right_btn, 0, ALIGN_CENTER | LEFT, 10)
        self.SetSizer(hbox)

    def decrease(self, event):
        self.value -= 1
        if self.min == self.value:
            self.left_btn.Disable()
        else:
            self.right_btn.Enable()
            self.left_btn.Enable()

        self.display.SetLabel(str(self.value))

        if self.listener is not None:
            self.listener()

        if event is not None:
            event.Skip()

    def increase(self, event):
        self.value += 1
        if self.max == self.value:
            self.right_btn.Disable()
        else:
            self.right_btn.Enable()
            self.left_btn.Enable()

        self.display.SetLabel(str(self.value))

        if self.listener is not None:
            self.listener()

        if event is not None:
            event.Skip()

    def set_value(self, value):
        if self.min is not None:
            value = max(value, self.min)

        if self.max is not None:
            value = min(value, self.max)

        self.value = value
        self.display.SetLabel(str(self.value))


class ErrorDialog(Dialog):
    def __init__(self, message, *args, **kw):
        super().__init__(*args, **kw)
        hbox = BoxSizer()
        message = NormalText(self, label=message)
        hbox.Add(message, 0, ALL | ALIGN_CENTER, 20)
        self.SetSizer(hbox)
        self.Fit()
        self.Center()
        self.ShowModal()


class NormalText(StaticText):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(Font(20, FONTFAMILY_DEFAULT, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))


class NormalButton(Button):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(Font(20, FONTFAMILY_DEFAULT, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))


class WatchText(StaticText):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(Font(30, FONTFAMILY_DEFAULT, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))


class NormalCaption(TextCtrl):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(Font(20, FONTFAMILY_DEFAULT, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))


class PreviewEntry(TextCtrl):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(Font(18, FONTFAMILY_MODERN, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))


class HelpText(StaticText):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetFont(Font(11, FONTFAMILY_MODERN, FONTSTYLE_NORMAL, FONTWEIGHT_NORMAL))


def get_hms(seconds):
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return h, m, s


def choose_file(parent, message, d=None):
    folder = FileDialog(parent, message=message, defaultFile='sample.txt', style=FD_SAVE)

    if folder.ShowModal() == ID_OK:
        return folder.GetPath()


def open_github():
    webopen('https://github.com/ryoTd0112')


def open_json_file(path):
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            ret = load(f)
    except (FileNotFoundError, TypeError):
        ret = None
    return ret


def open_txt_file(path):
    try:
        with open(path, mode='r', encoding='utf-8') as f:
            ret = f.read()
    except (FileNotFoundError, TypeError):
        ret = None

    return ret


def find_data_file(filename):
    try:
        if getattr(sys, 'frozen', False):
            datadir = dirname(sys.executable)
        else:
            datadir = dirname(__file__)
        ret = join(datadir, filename)
    except TypeError:
        ret = None

    return ret


def get_data_safety(dict_, key, default_value=None):
    try:
        ret = dict_[key] if (dict_ is not None) and (key in dict_) else default_value
    except TypeError:
        ret = default_value
        print('error')

    return ret


def main():
    app = App()
    MainWindow(parent=None, size=(WINDOW_WIDTH, WINDOW_HEIGHT))
    app.MainLoop()


if __name__ == "__main__":
    main()
