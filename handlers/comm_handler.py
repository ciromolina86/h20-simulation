import os
import datetime
import time
import threading
from pycomm3 import LogixDriver, CommError


class Logix_Manager:
    # Constructor for the class object
    # plc_group_size: group size of all plcs included in one group, which will take care by one thread
    #                 the reading of all plcs in one group is consecutive while each group is handled in multi-threads
    # group_read_cycle_ms: define the main reading cycle time (ms) for all groups (threads)
    # timeout_sec: define the timeout (sec)

    def __init__(self, plc_group_size: int = 5, group_read_cycle_ms: int = 500, timeout_sec: int = 2):
        self._group_size = plc_group_size  # How many PLCs want to include in one reading thread
        self._cycle_sec: float = group_read_cycle_ms / 1000  # reading cycle time (sec)
        self._timeout_sec = timeout_sec  # time out for reading
        self._plcs = {}
        self._thread = None
        self._finish = False
        self._count_cycle = 0

    # Method called when releasing resources

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    # Add the PLC configuration on the plcs main dict based on configuration dict
    # this method create also placeholder in main dict for latest values read
    # Example of cfg: {'plc': 'line1', 'ip': '192.168.10.190', 'tags': ['tag1','tag2','tag3']}

    def add_plc(self, cfg: dict):
        plc_name = cfg['plc']
        added = {'ip': cfg['ip'], 'tags': cfg['tags'], 'reconnect': 0}

        # added placeholder for values key, one for each tag
        lvalues = [None] * len(added['tags'])
        added['values'] = lvalues

        plc = None
        try:
            # Create the driver and open connection
            plc = LogixDriver(path=added['ip'], init_tags=False)
            # In case needed these steps individually to avoid issues when init_tags = True
            plc.open();
            plc.get_plc_info();
            plc.get_tag_list()
        except Exception as e:
            print('[ERROR] Added PLC failed', e)
        finally:
            added['driver'] = plc
            self._plcs[plc_name] = added

    # ****************************************************************************************
    # Check ping response to make sure can connect
    # return True if can ping otherwise return False
    # ****************************************************************************************
    def check_ping_plc(self, plc: str):
        """
        Check if can ping the ip address
        :param plc: plc name
        :return: True if success, False if not
        """
        try:
            ip_address = self._plcs[plc]['ip']
            # cmd = "ping -c 1 -W 1 " + ip_address # for Windows -n 1, for linux -c 1 -W 1
            cmd = "ping -n 1 " + ip_address  # for Windows -n 1, for linux -c 1 -W 1

            print("[Warn] Execute ping", cmd)
            response = os.system(cmd)  # try to ping only 1 time and timeout(-W) =1
            if response == 0:
                return True
            else:
                return False
        except Exception as e:
            print("[ERROR] ping failed, runtime error", e)
            return False

    # Get reconnect counter
    def get_reconnect_plc(self, plc: str):
        return self._plcs[plc]['reconnect']

    # reload driver if can ping it
    def reload_driver(self, plc: str):
        params = self._plcs[plc]
        if self.check_ping_plc(plc):
            self._plcs[plc]['driver'] = LogixDriver(path=params['ip'], init_tags=True)
        else:
            print('[ERROR] Cannot reload the driver for', plc, 'not pinging')

    # Check if the PLC is connected
    def is_connected(self, plc: str):
        return self._plcs[plc]['driver'].connected

    # Reconnect, close and open connection
    def reconnect(self, plc: str):
        try:
            self._plcs[plc]['reconnect'] += 1
            self._close(plc)
            self.reload_driver(plc)  # need to reload the driver, open only will not recovery
            self._open(plc)
        except Exception as e:
            print('[ERROR] Reconnecting error', e)

    # Start Main Reading Cycle Thread
    def start(self):
        print('[INFO] Start Reading')
        self._thread = threading.Thread(target=self._reading_cycle, daemon=True)
        # This thread is controlled by property _finish
        self._finish = False
        self._count_cycle = 0
        self._thread.start()
        # Waiting to finish first cycle to avoid getting null values on first reading
        self._wait_first_cycle()

    # Stop main reading cycle
    def stop(self):
        print('[INFO] Stop Reading')
        self._finish = True
        # When the reading cycle finished properly it will reset this flag
        while self._finish:
            pass

    # Open all PLC connections
    def open(self):
        for plc in self._plcs:
            self._open(plc)

    # Close all PLC connections
    def close(self):
        for plc in self._plcs:
            self._close(plc)

    # Read data from PLC and put results on the values key
    def read(self, plc: str):
        cfg = self._plcs[plc]
        try:
            tags_list = cfg['tags']
            len_tags = len(tags_list)
            if len_tags == 0:  # there is no tags to read
                print('[WARN] Read from', plc, 'no tags to read')
            else:
                tags = self._plcs[plc]['driver'].read(*tags_list)
                # check if the reading was one tag or multiple tags
                # if reading one tag in a list, only return tag attributes otherwise return list of tags attributes
                if len_tags == 1:
                    self._plcs[plc]['values'][0] = tags.value
                else:
                    for i in range(len_tags):
                        self._plcs[plc]['values'][i] = tags[i].value
        except Exception as e:
            print('[ERROR] Read from', plc, 'with error', e)
            self.reconnect(plc)  # try to recover

    # Read all tags from multiple PLCs
    def read_plcs(self, plcs: list):
        for plc in plcs:
            self.read(plc)

    # Get symbol table from plc
    def get_tags_list(self, plc: str):
        return self._plc[plc].get_tag_list()

    # get info from plc
    def get_plc_info(self, plc: str):
        return self._plc[plc].get_plc_info()

    # Get tags & its latest values in dict
    # return dict {<tag name>: < value>, ... }
    def get_tags(self, plc: str) -> dict:
        dic = {}
        index = 0
        for tag in self._plcs[plc]['tags']:
            dic[tag] = self._plcs[plc]['values'][index]
            index += 1
        return dic

    # Force read tags from the PLC, this is separated from the main reading cycle
    # usually it is not needed as long as the reading threading are running in background
    # return the dict {<tag name>: < value>, ... }
    def read_tags(self, plc: str) -> dict:
        self.read(plc=plc)
        return self.get_tags(plc=plc)

    # Reading Cycle method is called from a separated thread
    # This method perform the reading cycle in endless loop until finish when calling Stop
    def _reading_cycle(self):
        # while it is not finish the reading cycle (main reading thread)
        while not self._finish:
            start_time = time.time()
            self._run_threads()
            self._count_cycle += 1
            end_time = time.time()
            duration = end_time - start_time
            if duration < self._cycle_sec:
                time.sleep(self._cycle_sec - duration)
            else:
                time.sleep(0.001)
                print('[WARN] Overtime reading cycle by', duration - self._cycle_sec)

        # When finish closes all connections
        self.close()

        # Reset the finish flag to indicate the reading thread is done
        self._finish = False

    # Reading threads for all PLCs grouped
    def _run_threads(self):
        # print('[INFO] Calling Reading threads')
        threads = list()
        plc_list = list()
        key_list = list(self._plcs)
        # create all threads with its respective plc list to take care of
        i = 0  # index for plc keys
        c = 0  # counter for plc groups
        while i < len(key_list):
            plc_list.append(key_list[i])
            i += 1
            c += 1
            if c >= self._group_size:
                thr = threading.Thread(target=self.read_plcs, args=(plc_list,))
                thr.setDaemon(True)  # the main thread don't need to wait
                threads.append(thr)
                # init counter and plc list
                c = 0
                plc_list = list()

        # after the while loop to setup threads, check if there is any pending plc list
        # if any add into the threading
        if len(plc_list) > 0:
            thr = threading.Thread(target=self.read_plcs, args=(plc_list,))
            thr.setDaemon(True)  # the main thread don't need to wait
            threads.append(thr)

        # print('[INFO] Call run Total Threads',len(threads))
        # start threads
        for thr in threads:
            thr.start()

        # Wait for all threads to finish
        for thr in threads:
            thr.join(self._timeout_sec)
        # print('[INFO] Reading threads done')

    # Open Connection to the PLC
    def _open(self, plc: str):
        try:
            if self.check_ping_plc(plc):
                self._plcs[plc]['driver'].open()
            else:
                print('[ERROR] open failed from', plc, 'cannot ping')
        except Exception as e:
            print('[ERROR] open failed from', plc, 'with error', e)

    # Close Connection to the PLC
    def _close(self, plc: str):
        try:
            self._plcs[plc]['driver'].close()
        except Exception as e:
            print('[ERROR] close to', plc, 'with error', e)

    # Wait little bit a couple of reading cycle passed
    # This will guarantee the latest values are not null, if the tag name is correct
    def _wait_first_cycle(self):
        print('[INFO] Waiting finish first cycle')
        while self._count_cycle <= 1:
            time.sleep(0.1)


"""
# Example how to use it

mng = Logix_Manager(plc_group_size=2, group_read_cycle_ms=500, timeout_sec=3)  # Two PLCs will be handle by one thread
mng.add_plc(cfg={'plc': 'line1', 'ip': '192.168.10.45', 'tags': ['testSine', 'testBool']})
mng.add_plc(cfg={'plc': 'line2', 'ip': '192.168.10.45', 'tags': ['testSine', 'testBool']})
mng.add_plc(cfg={'plc': 'line3', 'ip': '192.168.10.45', 'tags': ['testSine', 'testBool']})

mng.start()
while (True):
    #print(mng.check_ping_plc('line1'))
    print(mng.get_tags('line1'))  # will get latest value as dict {<tag name>: <tag value>}
    tags = mng.get_tags('line2') # will get latest value as dict {<tag name>: <tag value>}
    print(mng.get_reconnect_plc('line1'), tags['testSine'], tags['testBool'])

mng.stop()
print('Done')
"""


class CLX_Manager:
    def __init__(self, ip_address: str = '192.168.1.10', cpu_slot: int = 0, eth_slot: int = 1):
        self._ip_address = ip_address
        self._cpu_slot = str(cpu_slot)
        self._eth_slot = str(eth_slot)
        self._path = '/'.join([self._ip_address, self._eth_slot, self._cpu_slot])
        self._plc = LogixDriver(self._path, init_tags=True)
        # print(self._path)

    # get info from plc
    def get_plc_info(self):
        with self._plc as plc:
            return plc.get_plc_info()

    # get tag list from plc
    def get_tag_list(self):
        with self._plc as plc:
            return plc.get_tag_list()

    def get_tag_list_json(self):
        with self._plc as plc:
            return plc.tags_json

    def read_single_tag(self, tag_name: str = 'testDINT'):
        # Reading a single tag returns a Tag object
        # e.g. Tag(tag='testDINT', value=20, type='DINT', error=None)

        with self._plc as plc:
            result = plc.read(tag_name)
            # print(result)
            if result.error is None:
                # print(f'{datetime.datetime.now()}\t|\tReading successfully from \t{tag_name}: {result.value:.2f}')
                return result.value
            else:
                print(f'{datetime.datetime.now()}\t|\tError reading from \t{tag_name}: {result.error}')
                return None

    def read_multiple_tags(self, tag_names: list = ['testDINT', 'testSine']):
        # Reading multiple tags returns a list of Tag objects
        # e.g. [Tag(tag='testDINT', value=20, type='DINT', error=None),
        #       Tag(tag='testSine', value=100.36, type='REAL', error=None)]

        values = []
        with self._plc as plc:
            results = plc.read(*tag_names)

            for tag_name, result in zip(tag_names, results):
                if result.error is None:
                    values.append(result.value)
                else:
                    print(f'Error reading {tag_name}: {result.error}')
                    values.append(None)

        return values

    def read_udt(self, inst_name: str = 'Tank1'):
        # Structures can be read as a whole, assuming that no attributes have External Access set to None.
        # Structure tags will be a single Tag object, but the value attribute will be a dict of {attribute: value}.
        # e.g. Tag(tag='Tank1', value={'Level': 100.5, 'Level_EU': "ft", 'Volume': 1000, 'Volume_EU': "gal"},
        #          type='udtTank', error=None)

        with self._plc as plc:
            return plc.read(inst_name)

    def write_single_tag(self, tag_name: str = 'testSine', tag_value=None):
        # Writing a single tag returns a single Tag object response
        # e.g. Tag(tag='testSine', value=100.5, type='REAL', error=None)

        with self._plc as plc:
            result = plc.write((tag_name, tag_value))
            # print(result)

        if result.error is None:
            # print(f'{datetime.datetime.now()}\t|\tWriting successfully to \t{tag_name}: {result.value:.2f}')
            return result.value
        else:
            print(f'{datetime.datetime.now()}\t|\tError writing to \t{tag_name}: {result.error}')
            return None

    def write_multiple_tags(self, tag_names: list = ['testSine', 'testDINT'], tag_values: list = [None, None]):
        # Writing multiple tags will return a list of Tag objects
        # e.g. [Tag(tag='testSine', value=25.2, type='REAL', error=None),
        #       Tag(tag='testDINT', value=20, type='DINT', error=None)]

        with self._plc as plc:
            data = list(zip(tag_names, tag_values))
            results = plc.write(*data)
            # print(type(result),result)

        for tag_name, result in zip(tag_names, results):
            if result.error is None:
                # print(f'{datetime.datetime.now()}\t|\tWriting successfully to \t{tag_name}: {result.value:.2f}')
                return result.value
            else:
                print(f'{datetime.datetime.now()}\t|\tError writing to \t{tag_name}: {result.error}')
                return None