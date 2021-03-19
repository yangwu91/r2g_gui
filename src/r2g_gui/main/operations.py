import os
import sys
import time
from copy import deepcopy
import json
import tempfile
from pathlib import Path
import subprocess
import webbrowser

from PyQt5 import QtCore, QtWidgets, QtGui
import docker

import r2g_gui
from r2g_gui.main import ui_main


r2g_image = "yangwu91/r2g:1.0.5"


class R2gMainWindow(QtWidgets.QMainWindow, ui_main.Ui_MainWindow):
    closeSignal = QtCore.pyqtSignal()

    def __init__(self):
        self.start_icon = QtGui.QIcon()
        self.start_icon.addPixmap(QtGui.QPixmap(
            "{}/images/start.png".format(r2g_gui.__path__[0])), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        self.stop_icon = QtGui.QIcon()
        self.stop_icon.addPixmap(QtGui.QPixmap(
            "{}/images/stop.png".format(r2g_gui.__path__[0])), QtGui.QIcon.Normal, QtGui.QIcon.Off
        )
        super(R2gMainWindow, self).__init__()
        self.setupUi(self)
        self.default = self.obtain_parameters()
        self.required = ["query", "sra"]
        self.elements = {
            "query": self.query,
            "query_file": self.query_file,
            "sra": self.sra,
            "program": self.program,
            "cut": self.cut,
            "max_num_seq": self.max_num_seq,
            "evalue": self.evalue,
            "filter": self.filter,
            "min_contig": self.min_contig,
            "trim": self.trim,
            "trim_param": self.trim_para,
            "stage": self.stage,
            "CPU": self.cpu,
            "max_memory": self.max_memory,
            "results": self.results,
            "outdir": self.outputdir,
        }
        self.wrong_parameters = {}
        self.user_param = {}
        self.r2g_backend = R2gDockerThread()
        self.docker_status = DockerStatus()
        self.docker_status.start()
        self.engine_version = "not available"
        self.connecter()
        self.show()

    def error_box(self, msg):
        QtWidgets.QMessageBox.critical(
            self,
            "Error!",
            msg,
            QtWidgets.QMessageBox.Abort
        )

    def info_box(self, msg):
        QtWidgets.QMessageBox.information(
            self,
            "Info",
            msg,
            QtWidgets.QMessageBox.Ok
        )

    def warning_box(self, msg):
        option = QtWidgets.QMessageBox.warning(
            self,
            "Warning",
            msg,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        return option

    def closeEvent(self, event):
        self.closeSignal.emit()

    def value_changed(self):
        current_param = deepcopy(self.obtain_parameters())
        if current_param != self.default:
            self.undo.setHidden(True)
            self.actionUndo.setEnabled(False)
            self.reset.setEnabled(True)
            self.actionRestore_to_defaults.setEnabled(True)
        else:
            self.undo.setVisible(True)
            self.actionUndo.setEnabled(True)
            self.reset.setEnabled(False)
            self.actionRestore_to_defaults.setEnabled(False)
        for p in self.required:
            if current_param[p] != self.default[p]:
                self.elements[p].setStyleSheet("")
        for p in self.wrong_parameters.keys():
            if current_param[p] != self.wrong_parameters[p]:
                self.elements[p].setStyleSheet("")
        # if os.access(current_param['query_file'], os.R_OK) and os.path.isfile(current_param['query_file']):
        #     try:
        #         with open(current_param['query_file'], "rt") as inf:
        #             self.query.setPlainText(inf.read())
        #    except Exception:
        #        pass

    def obtain_parameters(self):
        """obtain parameters from the UI windows, and then transfer them to r2g input format:
        r2g parameters:
        {'verbose': True, 'retry': 5, 'cleanup': False, 'outdir': 'S6K_q-aae_s-SRX885420_c-80.50_p-blastn',
        'browser': 'http://139.59.216.78:4444/wd/hub', 'proxy': None, 'sra': 'SRX885420',
        'query': 'AAEL018120-RE.S6K.fasta', 'program': 'blastn', 'max_num_seq': 1000, 'evalue': 0.001, 'cut': '80,50',
        'CPU': 16, 'max_memory': '4G', 'min_contig_length': 150, 'trim': False, 'stage': 'butterfly', 'docker': False,
        'chrome_proxy': None, 'firefox_proxy': None}
        """
        parameters = {
            "query": self.query.toPlainText(),
            "query_file": self.query_file.text(),  # not the r2g parameters
            "sra": self.sra.text(),
            "program": self.program.currentText(),  # needs to be re-formatted
            "cut": self.cut.text(),
            "max_num_seq": self.max_num_seq.text(),
            "evalue": self.evalue.text(),
            "filter": self.filter.checkState(),
            "min_contig": self.min_contig.text(),
            "trim": self.trim.checkState(),
            "trim_param": self.trim_para.text(),  # not the r2g parameters
            "stage": self.stage.currentText(),
            "CPU": self.cpu.text(),
            "max_memory": self.max_memory.text(),
            "results": self.results.text(),   # not the r2g parameters
            "outdir": self.outputdir.text(),  # needs to be re-formatted
            "verbose": False,
            "retry": 5,
            "cleanup": False,
            "browser": None,
            "proxy": None,
            "docker": True,
            'chrome_proxy': None,
            'firefox_proxy': None,
        }
        return parameters

    def check_parameters(self, parameters):
        passed = True
        for p in self.required:
            if parameters[p] == self.default[p]:
                self.elements[p].setStyleSheet("background-color: rgb(255, 139, 190);")
                passed = False
        return passed

    def set_parameters(self, parameters):
        self.query.setPlainText(parameters.get('query', ""))
        self.query_file.setText(parameters.get('query_file', ""))
        self.sra.setText(parameters.get('sra', ""))
        self.program.setCurrentText(parameters.get('program', "blastn - megablast (highly similar sequences"))
        self.cut.setText(parameters.get('cut', ""))
        self.max_num_seq.setText(parameters.get('max_num_seq', ""))
        self.evalue.setText(parameters.get('evalue', ""))
        self.filter.setChecked(parameters.get('filter', True))
        self.min_contig.setText(parameters.get('min_contig', ""))
        self.trim.setChecked(parameters.get("trim", True))
        self.trim_para.setText(parameters.get('trim_para', ""))
        self.stage.setCurrentText(parameters.get("stage", "butterfly"))
        self.cpu.setText(parameters.get("CPU", ""))
        self.max_memory.setText(parameters.get("max_memory", ""))
        self.results.setText(parameters.get("results", ""))
        self.outputdir.setText(parameters.get("outdir", ""))

    def openfile(self):
        opendir = os.getcwd()
        query_file = self.query_file.text()
        if len(query_file) > 0:
            if os.path.isfile(query_file):
                opendir = os.path.split(query_file)[0]
            elif os.path.isdir(query_file):
                opendir = query_file
        # filename, filetype
        openfile_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Please choose a sequence file in FASTA format",
            opendir,
            "FASTA Files (*.fasta *.fa *.fna *.faa *.txt);;All Files (*)"
        )
        if len(openfile_name) > 0:
            self.query_file.setText(openfile_name)
            with open(openfile_name, 'r') as inf:
                self.query.setPlainText(inf.read())

    def select_dir(self):
        outdir = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Please select a directory to store results",
        )
        self.outputdir.setText(outdir)

    def load_param_file(self):
        param_file, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Load parameters from a json file",
            str(Path.home()),  # os.getcwd(),
            "JSON Files (*.json *.txt);;All Files (*)"
        )
        if len(param_file) > 0:
            with open(param_file, 'r') as inf:
                try:
                    param_json = json.load(inf)
                except Exception as err:
                    self.error_box("Couldn't load parameters from the file \"{}\". {}".format(param_file, err))
                else:
                    self.set_parameters(param_json)

    def save_param(self):
        param_file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save parameters as...",
            str(Path.home()),  # os.getcwd(),
            "JSON Files (*.json *.txt);;All Files (*)"
        )
        if len(param_file) > 0:
            extension = os.path.splitext(param_file)[-1]
            if len(extension) == 0:
                param_file += ".json"
            try:
                with open(param_file, 'w') as outf:
                    self.user_param = self.obtain_parameters()
                    json.dump(self.user_param, outf, indent=4, separators=(",", ": "))
            except Exception as err:
                self.error_box("Couldn't save parameters as the file \"{}\". {}".format(param_file, err),)
            else:
                self.info_box("Saved parameters as the file \"{}\".".format(param_file))

    def enable_trim(self):
        if self.trim.isChecked():
            self.lbl_trimpara.setEnabled(True)
            self.trim_para.setEnabled(True)
        else:
            self.lbl_trimpara.setEnabled(False)
            self.trim_para.setEnabled(False)

    def exit_(self):
        if self.submit.text() == "Stop!":
            warning = self.warning_box("The job is running. Are you sure about exiting?")
            if warning == QtWidgets.QMessageBox.Yes:
                self.r2g_backend.stop_()
                self.r2g_backend.quit()
                self.docker_status.quit()
                sys.exit(0)
            else:
                pass
        self.r2g_backend.stop_()
        self.r2g_backend.quit()
        self.docker_status.quit()
        sys.exit(0)

    def check_query(self):
        query = self.query.toPlainText()
        # Show the length of the query:
        seq = query.strip().splitlines()
        if len(seq) > 0:
            if seq[0][0] == ">":
                seq = ''.join(seq[1:])
            else:
                seq = ''.join(seq)
            seq = ''.join(seq.strip().split())
        self.lbl_query_len.setText("{} sequences".format(len(seq)))

    def activate_boxes(self, panel):
        if panel == "output":
            self.aligning_box.setEnabled(False)
            self.assembling_box.setEnabled(False)
            self.reset.setEnabled(False)
            self.results_box.setEnabled(False)
            self.query.setEnabled(False)
            self.output_box.setEnabled(True)
            self.output_log.setEnabled(True)
            self.output_log.clear()
            self.submit.setText("Stop!")
            self.submit.setIcon(self.stop_icon)
        elif panel == "input":
            self.submit.setText("Start!")
            self.submit.setIcon(self.start_icon)
            # self.output_log.setText("Stopped.")
            self.aligning_box.setEnabled(True)
            self.assembling_box.setEnabled(True)
            self.reset.setEnabled(True)
            # self.reset.setEnabled(True)
            self.results_box.setEnabled(True)
            self.query.setEnabled(True)
            # self.output_box.setEnabled(False)
            # self.lbl_mode.setText("Stopped.")

    def call_r2g(self):
        if self.submit.text() == "Start!":
            parameters = self.obtain_parameters()
            if parameters['verbose']:
                self.output_log.append(str(parameters))
            if self.check_parameters(parameters):
                try:
                    self.activate_boxes("output")
                    self.r2g_backend.preflight(parameters)
                except (SystemError, IOError) as err:
                    self.error_box(str(err))
                    self.activate_boxes("input")
                else:
                    self.r2g_backend.start()
            else:
                self.error_box("The highlighted parameters are required.")

        elif self.submit.text() == "Stop!":
            warning = self.warning_box("Are you sure about stopping the running job?")
            if warning == QtWidgets.QMessageBox.Yes:
                self.r2g_backend.stop_()
                self.r2g_backend.quit()
                self.activate_boxes("input")
                self.output_log.append(
                    "[{}] Terminated by user.".format(time.strftime("%m-%d-%Y %H:%M:%S", time.localtime()))
                )

    def clear_default(self, default_value):
        self.sender().setReadOnly(False)
        if self.sender().text() == default_value:
            self.sender().clear()

    def set_default(self, default_value):
        self.sender().setReadOnly(True)
        if len(self.sender().text().strip()) < 1:
            self.sender().setText(default_value)

    def reset_para(self):
        self.user_param = self.obtain_parameters()
        if self.user_param != self.default:
            self.undo.setVisible(True)
            self.actionUndo.setEnabled(True)
            self.reset.setEnabled(False)
            self.actionRestore_to_defaults.setEnabled(False)
            self.set_parameters(self.default)

    def undo_para(self):
        self.undo.setHidden(True)
        self.actionUndo.setEnabled(False)
        self.set_parameters(self.user_param)

    def print_log(self, log):
        """transfer bash color to html color:
        """
        # TODO
        # log = "<font color=\"#FF0000\">" + "warning" + "</font> " + " ???"
        self.output_log.append(log)

    def print_status(self, status):
        # Status code:
        # 0. ready to go
        # 1. running
        # 2. pulling
        # 3. not started
        code, status = status.split(". ", 1)
        self.lbl_mode.setText("Docker engine: {}.".format(status))
        if code in ["0", "1"]:
            self.submit.setEnabled(True)
        else:
            self.submit.setEnabled(False)
        if code == "0":
            self.actionUpdate_the_r2g_engine.setEnabled(True)
            self.actionUpdate_the_r2g_engine.setText("Update the r2g engine")
        elif code == "2":
            self.actionUpdate_the_r2g_engine.setEnabled(False)
            self.actionUpdate_the_r2g_engine.setText("Pulling the latest {} image...".format(r2g_image))
        else:
            self.actionUpdate_the_r2g_engine.setEnabled(False)
            self.actionUpdate_the_r2g_engine.setText("Update the r2g engine")

    def housekeeping(self, done_msg):
        if done_msg != "0":
            self.error_box("Calling r2g failed. {}".format(done_msg))
        else:
            self.info_box("Calling r2g done.")
            self.activate_boxes("input")

    def raise_element_error(self, element):
        self.wrong_parameters[element] = deepcopy(self.obtain_parameters()[element])
        self.elements[element].setStyleSheet("background-color: rgb(255, 139, 190);")

    def keep_engine_version(self, version):
        self.engine_version = version

    def show_about(self):
        self.info_box(
            "{}\nAuthor: {} ({})\nHome: {}\nR2g GUI version: {}\nR2g Docker engine: {}\n{}\n".format(
                r2g_gui.__full_name__,
                r2g_gui.__author__, r2g_gui.__author_email__,
                r2g_gui.__url__,
                r2g_gui.__version__,
                self.engine_version,
                r2g_gui.__copyright__
            )
        )

    def show_help(self):
        webbrowser.open(r2g_gui.__url__)
        # self.info_box("Constructing...\nPlease visit: {}".format(r2g_gui.__url__))

    def update_engine(self, force=False):
        self.actionUpdate_the_r2g_engine.setEnabled(False)
        self.actionUpdate_the_r2g_engine.setText("Pulling the latest {} image...".format(r2g_image))
        self.print_status("2. pulling the {} image..".format(r2g_image))
        self.docker_status.quit()
        try:
            client = docker.from_env()
            if force:
                client.images.remove(r2g_image, force=True)
            client.images.pull(r2g_image)
        except docker.errors.DockerException:
            self.warning_box("The Docker has not been started yet.")
        self.print_status("0. ready to go".format(r2g_image))
        self.docker_status.start()
        self.info_box("The {} image is updated.".format(r2g_image))
        self.actionUpdate_the_r2g_engine.setEnabled(True)
        self.actionUpdate_the_r2g_engine.setText("Update the r2g engine")

    def connecter(self):
        # value changed:
        self.query.textChanged.connect(self.value_changed)
        self.query_file.textChanged.connect(self.value_changed)
        self.sra.textChanged.connect(self.value_changed)
        self.cut.textChanged.connect(self.value_changed)
        self.max_num_seq.textChanged.connect(self.value_changed)
        self.evalue.textChanged.connect(self.value_changed)
        self.min_contig.textChanged.connect(self.value_changed)
        self.trim_para.textChanged.connect(self.value_changed)
        self.stage.currentTextChanged.connect(self.value_changed)
        self.cpu.textChanged.connect(self.value_changed)
        self.max_memory.textChanged.connect(self.value_changed)
        self.results.textChanged.connect(self.value_changed)
        self.outputdir.textChanged.connect(self.value_changed)
        self.program.currentTextChanged.connect(self.value_changed)
        self.trim.stateChanged.connect(self.value_changed)
        # choose a query file:
        self.browser_file_button.clicked.connect(self.openfile)
        # select an output dir:
        self.browser_outputdir_button.clicked.connect(self.select_dir)
        # trim or not:
        self.trim.stateChanged.connect(self.enable_trim)
        # submit to run or stop:
        self.submit.clicked.connect(self.call_r2g)
        # exit:
        self.actionExit.triggered.connect(self.exit_)
        self.closeSignal.connect(self.exit_)
        # check the query sequence:
        self.query.textChanged.connect(self.check_query)
        # clear the default value:
        self.query.FocusInSignal.connect(self.clear_default)
        self.query.FocusOutSignal.connect(self.set_default)
        self.cut.FocusInSignal.connect(self.clear_default)
        self.cut.FocusOutSignal.connect(self.set_default)
        self.max_num_seq.FocusInSignal.connect(self.clear_default)
        self.max_num_seq.FocusOutSignal.connect(self.set_default)
        self.evalue.FocusInSignal.connect(self.clear_default)
        self.evalue.FocusOutSignal.connect(self.set_default)
        self.min_contig.FocusInSignal.connect(self.clear_default)
        self.min_contig.FocusOutSignal.connect(self.set_default)
        self.cpu.FocusInSignal.connect(self.clear_default)
        self.cpu.FocusOutSignal.connect(self.set_default)
        self.max_memory.FocusInSignal.connect(self.clear_default)
        self.max_memory.FocusOutSignal.connect(self.set_default)
        # restore and undo parameters:
        self.reset.clicked.connect(self.reset_para)
        self.actionRestore_to_defaults.triggered.connect(self.reset_para)
        self.undo.clicked.connect(self.undo_para)
        self.actionUndo.triggered.connect(self.undo_para)
        # save and load parameters from files:
        self.actionImport_parameters.triggered.connect(self.load_param_file)
        self.actionExport_parameters.triggered.connect(self.save_param)
        # return logs from the r2g backend thread:
        self.r2g_backend.outputSignal.connect(self.print_log)
        self.r2g_backend.doneSignal.connect(self.housekeeping)
        self.r2g_backend.errorSignal.connect(self.raise_element_error)
        # check and print docker status:
        self.docker_status.statusSignal.connect(self.print_status)
        self.docker_status.versionSignal.connect(self.keep_engine_version)
        # Others:
        self.actionAbout_r2g.triggered.connect(self.show_about)
        self.actionAbout.triggered.connect(self.show_help)
        self.actionUpdate_the_r2g_engine.triggered.connect(self.update_engine)


class R2gDockerThread(QtCore.QThread):
    outputSignal = QtCore.pyqtSignal(str)
    errorSignal = QtCore.pyqtSignal(str)
    doneSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(R2gDockerThread, self).__init__(parent)
        self.backend_mode = ""
        # try:
        #     import r2g
        #     self.backend_mode = "local"
        # except ModuleNotFoundError:
        #     self.backend_mode = "docker"
        self.parameters = {}
        # self.cmd = ["r2g", "--help"]
        self.cmd = []
        self.r2g_docker = None
        self.container = None
        self.workspace = None
        self.query_tmp_name = None

    def preflight(self, parameters):
        self.parameters = parameters
        try:
            self.r2g_docker = docker.from_env()
        except Exception as err:
            raise SystemError(
                "Could not connect to the Docker engine.\n"
                "Please follow the instruction (https://docs.docker.com/get-docker/) to installed the Docker, "
                "and then initiate the Docker engine before hit the start button.\n{}".format(err)
            )
        else:
            # configure the program:
            programs = {
                "blastn - megablast (highly similar sequences)": "megablast",
                "blastn - discontiguous megablast (more dissimiliar sequences)": "discomegablast",
                "blastn (nucleotide against nucleotide, return somewhat similar sequences)": "blastn",
                "tblastn (protein against nucleotide)": "tblastn",
                "tblastx (translated nucleotide against translated nucleotide)": "blastx"
            }
            self.cmd += ["--program", programs[self.parameters["program"]]]

            # configure the output dir and query:
            self.workspace = os.path.join(parameters["outdir"], parameters["results"])
            try:
                os.mkdir(self.workspace, 0o750)
            except (FileExistsError, PermissionError):
                if not os.access(self.workspace, os.W_OK):
                    self.errorSignal.emit("outdir")
                    raise IOError('{} is not writable.'.format(self.workspace))
            finally:
                with tempfile.NamedTemporaryFile(
                    "w+t", suffix=".fasta", prefix="query_tmp", dir=self.workspace, delete=False
                ) as query_tmp:
                    query_tmp.write(self.parameters['query'])
                    self.query_tmp_name = os.path.split(query_tmp.name)[-1]
                    self.cmd += [
                        "--query", "/workspace/{}/{}".format(self.parameters['results'], self.query_tmp_name),
                        "--outdir", "/workspace/{}".format(self.parameters['results'])
                    ]
            # configure other parameters:
            if self.parameters.get('trim', True) is True:
                self.cmd += ['--trim', ]
                if len(parameters.get("trim_para", "")) > 0:
                    self.cmd += [parameters["trim"], ]
            self.cmd += [
                "--sra", parameters["sra"],
                "--max_num_seq", parameters["max_num_seq"],
                "--evalue", parameters["evalue"],
                "--cut", parameters["cut"],
                "--CPU", parameters["CPU"],
                "--max_memory", parameters["max_memory"]+"G",
                "--min_contig_length", parameters["min_contig"],
                "--stage", parameters["stage"].split()[0].strip(),
            ]
            if parameters["verbose"]:
                self.cmd.append("--verbose")

    def run(self):
        self.outputSignal.emit(" ".join(self.cmd))
        try:
            uid = subprocess.check_output(['id', '-u'], shell=False).decode('utf-8').strip()
        except FileNotFoundError:  # On Windows, $UID is not necessary.
            uid = "1001"  # It's better not to run using root
        self.container = self.r2g_docker.containers.run(
            r2g_image,
            self.cmd,
            detach=True,
            auto_remove=True,
            shm_size=self.parameters['max_memory']+"G",
            user=uid,
            volumes={self.parameters['outdir']: {"bind": "/workspace", "mode": "rw"}}
        )
        try:
            for line in self.container.logs(stream=True, stderr=True, follow=True):
                self.outputSignal.emit(line.decode('utf-8').rstrip())
        except Exception as err:
            self.doneSignal.emit(err)
        else:
            self.doneSignal.emit('0')
        try:
            os.remove(os.path.join(self.workspace, self.query_tmp_name))
        except (FileNotFoundError, TypeError):
            pass

    def stop_(self):
        try:
            self.container.stop()
        except Exception:
            pass
        try:
            os.remove(os.path.join(self.workspace, self.query_tmp_name))
        except (FileNotFoundError, TypeError):
            pass


class DockerStatus(QtCore.QThread):
    statusSignal = QtCore.pyqtSignal(str)
    versionSignal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(DockerStatus, self).__init__(parent)

    def run(self):
        while True:
            try:
                client = docker.from_env()
            except docker.errors.DockerException:
                self.statusSignal.emit("3. not started yet")
                self.versionSignal.emit("not available")
                time.sleep(10)
            else:
                try:
                    client.images.get(r2g_image)
                except docker.errors.ImageNotFound:
                    self.statusSignal.emit("2. pulling the {} image..".format(r2g_image))
                    self.versionSignal.emit("not available")
                    client.images.pull(r2g_image)
                else:
                    containers = client.containers.list()
                    running = False
                    if len(containers) > 0:
                        for c in containers:
                            image = c.attrs["Config"]['Image']
                            if image == r2g_image:
                                running = True
                    if running:
                        self.statusSignal.emit("1. r2g is running..")
                    else:
                        self.statusSignal.emit("0. ready to go")
                    try:
                        version = client.containers.run(r2g_image, "--version", auto_remove=True)
                        version = version.decode('utf-8').strip('\n').split('\n')[-1].split(" ")[-1]
                        self.versionSignal.emit(version)
                    except docker.errors.NotFound:
                        pass
                    time.sleep(10)
