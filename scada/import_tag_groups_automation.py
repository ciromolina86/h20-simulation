import pyautogui
from pyautogui import Point
import time
import os, sys


def open_terminal():
    pyautogui.PAUSE = 2.0
    pyautogui.hotkey('win', 'r')
    pyautogui.press('enter')
    pyautogui.hotkey(list('ipconfig'))
    # pyautogui.hotkey('alt', 'f4')
    # pyautogui.hotkey('alt', 'f4')
    pyautogui.press('enter')


def show_mouse_pos():
    for i in range(10):
        mouse_pos = pyautogui.position()
        # print(f'{10-i} - {mouse_pos}', end='\r')
        print(f'{10 - i} - {mouse_pos}')
        sys.stdout.flush()
        time.sleep(1)

    return mouse_pos


def main():
    print('please, move mouse to screen position where typing should occur.')
    mouse_pos = show_mouse_pos()
    print(f'mouse position recorded was {mouse_pos}')
    answer = input("enter 'Y' to confirm, 'N' to cancel: ")

    if answer.lower() == 'y':
        path = input('enter path of txt file to be typed: ')
        # path = "typing-data.txt"

        if os.path.isfile(path):
            pyautogui.click(mouse_pos)

            for line in open(path, "r"):
                pyautogui.typewrite(line)

    else:
        pass


def steps_sequence(instance):
    pyautogui.PAUSE = 1.5
    # step 1
    pyautogui.click(Point(x=2265, y=121))  # select window
    # step 2
    pyautogui.hotkey('ctrl', 'n')  # select new file
    # pyautogui.click(Point(x=2157, y=177))  # select new file
    # pyautogui.click(Point(x=2091, y=226))  # select Symbol field
    # step 3
    pyautogui.typewrite('EquipmentName')
    # step 4
    pyautogui.hotkey('tab')
    pyautogui.typewrite(instance)
    # step 5
    pyautogui.hotkey('ctrl', 's')
    pyautogui.typewrite(instance)
    pyautogui.press('enter')


if __name__ == '__main__':
    instances = ['LIT_15_11', 'FIT_30_04', 'PIT_15_12', 'FIT_15_12', 'AIT_15_11A', 'AIT_15_11B_1', 'AIT_15_11B_2',
                 'AIT_15_11C', 'AIT_30_01A', 'AIT_30_01B', 'AIT_30_01C', 'AIT_30_01D', 'FIT_30_03', 'FIT_30_01',
                 'FIT_30_02', 'LIT_30_01', 'PIT_30_01', 'AIT_30_01E', 'AIT_30_01F', 'AIT_30_01G_1', 'AIT_30_01H',
                 'AIT_30_01I', 'AIT_30_01J', 'AIT_30_01K', 'PIT_30_11', 'AIT_30_11A', 'AIT_30_11B_2', 'AIT_30_11C',
                 'AIT_30_11D', 'AIT_30_11E', 'AIT_30_11G', 'AIT_30_11F', 'AIT_30_11B_1', 'FIT_30_62', 'FIT_30_31',
                 'PIT_70_12', 'PIT_70_11', 'FIT_70_11', 'FIT_70_12', 'PIT_70_13', 'PDIT_70_11', 'PDIT_70_12',
                 'PDIT_70_13', 'FIT_40_41', 'LIT_40_42', 'AIT_30_51A', 'AIT_30_51B', 'LIT_40_41', 'LIT_30_51',
                 'FIT_40_51', 'PIT_40_51', 'LIT_70_31', 'LIT_SAMPLE', 'FIT_70_41', 'PIT_70_41', 'LIT_70_51',
                 'PIT_70_52', 'PIT_70_51', 'AIT_30_21', 'PIT_30_31', 'LIT_SAMPLE1', 'TIT_30_41', 'TIT_30_42',
                 'TIT_30_44', 'AIT_30_44', 'FIT_30_45', 'LIT_30_41', 'LIT_30_42', 'PIT_30_45', 'AIT_40_01A',
                 'PIT_40_01', 'PIT_40_02', 'PIT_40_03', 'AIT_40_01B_1', 'AIT_40_01B_2', 'AIT_40_01C', 'AIT_40_02A',
                 'AIT_40_02B', 'AIT_40_02C', 'AIT_40_02D', 'AIT_40_11A', 'AIT_40_12A', 'AIT_40_13A', 'FIT_40_12A',
                 'PIT_40_11A', 'PIT_40_11B', 'PIT_40_11C', 'PIT_40_12A', 'PIT_40_13A', 'PIT_40_13B', 'PIT_40_11AA',
                 'PIT_40_11BA', 'AIT_40_11B', 'FIT_40_13A', 'PIT_40_14', 'FIT_40_14', 'AIT_40_14', 'AIT_40_03A',
                 'AIT_40_03B', 'FIT_40_15', 'FIT_40_16', 'PIT_40_15A', 'AIT_40_15', 'FIT_40_21', 'PIT_40_21',
                 'LIT_40_21', 'AIT_40_32', 'FIT_40_32', 'LIT_40_31', 'LIT_40_32', 'PIT_40_32', 'TIT_40_32', 'TIT_40_33',
                 'TIT_40_31', 'AIT_40_31', 'AIT_40_41A', 'AIT_40_41B', 'AIT_40_51A', 'AIT_40_51B', 'AIT_40_51C_1',
                 'AIT_40_51C_2', 'FIT_40_52', 'PIT_40_52', 'AIT_30_01G_2', 'FIT_50_11', 'FIT_50_12', 'FIT_50_13',
                 'AIT_50_11A', 'AIT_50_11B', 'AIT_50_11C', 'AIT_50_11D', 'AIT_50_11E', 'AIT_50_11F', 'AIT_50_11G',
                 'AIT_50_11H', 'AIT_70_31A_1', 'AIT_70_31A_2', 'AIT_70_31B', 'AIT_70_31D', 'AIT_70_31C_1',
                 'AIT_70_31C_2', 'AIT_70_31E', 'AIT_70_31F', 'AIT_70_31H', 'AIT_70_51A', 'AIT_70_51B', 'AIT_70_51C',
                 'AIT_70_51E', 'AIT_70_52A', 'AIT_70_52C', 'AIT_70_52D', 'AIT_70_52E_1', 'AIT_70_52E_2', 'AIT_70_11A_1',
                 'AIT_70_11A_2', 'AIT_70_11B', 'AIT_70_11C', 'AIT_70_11D', 'LIT_80_11', 'WIT_80_51', 'WIT_80_52',
                 'LIT_80_21', 'LIT_80_31', 'LIT_80_61', 'WIT_80_71', 'WIT_80_72', 'WIT_80_41', 'WIT_80_42', 'WIT_80_81',
                 'WIT_80_82', 'FIT_90_11']

    for instance in instances:
        print(instance)
        steps_sequence(instance)

    # show_mouse_pos()
    # open_terminal()
