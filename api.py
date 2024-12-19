from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWebEngineWidgets import QWebEngineView
import requests
import json
import os
from threading import Thread
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QFormLayout, QLineEdit, QPushButton
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

CONFIG_FILE = "config.json"

class RestApiTester(QtWidgets.QMainWindow):
    request_signal = QtCore.pyqtSignal(str, str, str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ServiceNow REST API Tester")
        self.setGeometry(100, 100, 1200, 900)
        self.setStyleSheet("background-color: #2d2d2d; color: #ffffff;")

        # Initialize variables
        self.config = self.load_config()

        # Initialize UI components
        self.create_widgets()

        # Connect the request signal
        self.request_signal.connect(self.perform_request)

    def create_widgets(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # Endpoint URL Section
        url_layout = QtWidgets.QHBoxLayout()
        url_label = QtWidgets.QLabel("Endpoint URL:")
        self.url_entry = QtWidgets.QLineEdit()
        self.url_entry.setText(self.config.get("url", ""))
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_entry)
        layout.addLayout(url_layout)

        # HTTP Method Section
        method_layout = QtWidgets.QHBoxLayout()
        method_label = QtWidgets.QLabel("HTTP Method:")
        self.method_combo = QtWidgets.QComboBox()
        self.method_combo.addItems(["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
        self.method_combo.setCurrentText(self.config.get("method", "POST"))
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)

        # Tabs for Configuration
        self.tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.tab_widget)

        # Headers Tab
        headers_tab = QtWidgets.QWidget()
        headers_layout = QtWidgets.QVBoxLayout(headers_tab)
        headers_label = QtWidgets.QLabel("Headers (JSON format):")
        self.headers_editor = QWebEngineView()
        self.headers_editor.setHtml(self.get_ace_editor_html(self.config.get("headers", "{}")))
        headers_layout.addWidget(headers_label)
        headers_layout.addWidget(self.headers_editor)
        self.tab_widget.addTab(headers_tab, "Headers")

        # Payload Tab
        payload_tab = QtWidgets.QWidget()
        payload_layout = QtWidgets.QVBoxLayout(payload_tab)
        self.payload_editor = QWebEngineView()
        self.payload_editor.setHtml(self.get_ace_editor_html(self.config.get("payload", "{}")))
        payload_layout.addWidget(self.payload_editor)
        self.tab_widget.addTab(payload_tab, "Payload")

        # Payload Buttons
        payload_buttons_layout = QtWidgets.QHBoxLayout()
        format_button = QtWidgets.QPushButton("Format JSON Payload")
        format_button.clicked.connect(self.format_json_payload)
        template_button = QtWidgets.QPushButton("Insert Template")
        template_button.clicked.connect(self.insert_template)
        payload_buttons_layout.addWidget(format_button)
        payload_buttons_layout.addWidget(template_button)
        payload_layout.addLayout(payload_buttons_layout)

        # Authentication Tab
        auth_tab = QtWidgets.QWidget()
        auth_layout = QtWidgets.QGridLayout(auth_tab)
        auth_label = QtWidgets.QLabel("Authentication:")
        self.auth_combo = QtWidgets.QComboBox()
        self.auth_combo.addItems(["None", "Basic", "Bearer Token"])
        self.auth_combo.setCurrentText(self.config.get("auth_type", "Basic"))
        self.auth_combo.currentIndexChanged.connect(self.toggle_auth_fields)
        auth_layout.addWidget(auth_label, 0, 0)
        auth_layout.addWidget(self.auth_combo, 0, 1)

        # Username and Password Fields
        self.username_label = QtWidgets.QLabel("Username:")
        self.username_entry = QtWidgets.QLineEdit()
        self.username_entry.setText(self.config.get("username", ""))
        self.password_label = QtWidgets.QLabel("Password:")
        self.password_entry = QtWidgets.QLineEdit()
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.password_entry.setText(self.config.get("password", ""))
        auth_layout.addWidget(self.username_label, 1, 0)
        auth_layout.addWidget(self.username_entry, 1, 1)
        auth_layout.addWidget(self.password_label, 2, 0)
        auth_layout.addWidget(self.password_entry, 2, 1)

        # Bearer Token Field
        self.token_label = QtWidgets.QLabel("Bearer Token:")
        self.token_entry = QtWidgets.QLineEdit()
        self.token_entry.setText(self.config.get("token", ""))
        auth_layout.addWidget(self.token_label, 3, 0)
        auth_layout.addWidget(self.token_entry, 3, 1)

        self.tab_widget.addTab(auth_tab, "Authentication")
        self.toggle_auth_fields()

        # Send Request Button
        send_button = QtWidgets.QPushButton("Send Request")
        send_button.clicked.connect(self.send_request)
        layout.addWidget(send_button)

        # Response Section
        response_label = QtWidgets.QLabel("Response:")
        layout.addWidget(response_label)

        # Response Tabs (Editor and Tree View)
        self.response_tab_widget = QtWidgets.QTabWidget()
        layout.addWidget(self.response_tab_widget)

        # Response Editor
        response_editor_tab = QtWidgets.QWidget()
        response_editor_layout = QtWidgets.QVBoxLayout(response_editor_tab)
        self.response_editor = QWebEngineView()
        self.response_editor.setHtml(self.get_ace_editor_html())
        response_editor_layout.addWidget(self.response_editor)
        self.response_tab_widget.addTab(response_editor_tab, "Raw Response")

        # Response Tree View
        response_tree_tab = QtWidgets.QWidget()
        response_tree_layout = QtWidgets.QVBoxLayout(response_tree_tab)
        self.response_tree = QTreeWidget()
        self.response_tree.setHeaderLabel("Response Structure")
        response_tree_layout.addWidget(self.response_tree)
        self.response_tab_widget.addTab(response_tree_tab, "Tree View")

        # Response Visualization Tab
        response_visual_tab = QtWidgets.QWidget()
        response_visual_layout = QtWidgets.QVBoxLayout(response_visual_tab)
        self.response_visual_button = QPushButton("Visualize Response Data")
        self.response_visual_button.clicked.connect(self.visualize_response)
        response_visual_layout.addWidget(self.response_visual_button)
        self.response_visual_label = QtWidgets.QLabel()
        response_visual_layout.addWidget(self.response_visual_label)
        self.response_tab_widget.addTab(response_visual_tab, "Visualization")

    def toggle_auth_fields(self):
        auth_type = self.auth_combo.currentText()
        if auth_type == "Basic":
            self.username_label.show()
            self.username_entry.show()
            self.password_label.show()
            self.password_entry.show()
            self.token_label.hide()
            self.token_entry.hide()
        elif auth_type == "Bearer Token":
            self.username_label.hide()
            self.username_entry.hide()
            self.password_label.hide()
            self.password_entry.hide()
            self.token_label.show()
            self.token_entry.show()
        else:
            self.username_label.hide()
            self.username_entry.hide()
            self.password_label.hide()
            self.password_entry.hide()
            self.token_label.hide()
            self.token_entry.hide()

    def format_json_payload(self):
        self.payload_editor.page().runJavaScript("editor.getValue()", self.on_format_payload)

    def on_format_payload(self, payload):
        try:
            formatted_payload = json.dumps(json.loads(payload), indent=4)
            self.payload_editor.page().runJavaScript(f"editor.setValue({json.dumps(formatted_payload)})")
        except json.JSONDecodeError as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Invalid JSON: {str(e)}")

    def insert_template(self):
        self.config = self.load_config()  # Reload config to get updated templates
        templates = self.config.get("templates", {
            "Create Incident": {
                "short_description": "Short description of the incident",
                "priority": "2",
                "category": "network",
                "subcategory": "WAN"
            },
            "Update Change Request": {
                "change_id": "CHG1234567",
                "description": "Updated description for change request",
                "state": "in progress"
            }
        })
        template_keys = list(templates.keys())
        template, ok = QtWidgets.QInputDialog.getItem(self, "Select Template", "Available Templates:", template_keys, 0, False)
        if ok and template:
            template_content = json.dumps(templates[template], indent=4)
            self.payload_editor.page().runJavaScript(f"editor.setValue({json.dumps(template_content)})")

    def send_request(self):
        url = self.url_entry.text().strip()
        method = self.method_combo.currentText()

        # Get Headers from Ace Editor
        self.headers_editor.page().runJavaScript("editor.getValue()", lambda headers_input: self.get_payload_and_send(url, method, headers_input))

    def get_payload_and_send(self, url, method, headers_input):
        # Get Payload from Ace Editor
        self.payload_editor.page().runJavaScript("editor.getValue()", lambda payload_input: self.request_signal.emit(url, method, headers_input, payload_input))

    def perform_request(self, url, method, headers_input, payload_input):
        from threading import Thread  # Fixing missing import
        auth_type = self.auth_combo.currentText()

        # Validate URL
        if not url:
            QtWidgets.QMessageBox.critical(self, "Error", "Endpoint URL is required.")
            return

        # Validate and Parse Headers
        headers = {}
        if headers_input:
            try:
                headers = json.loads(headers_input)
            except json.JSONDecodeError:
                QtWidgets.QMessageBox.critical(self, "Error", "Headers must be in valid JSON format.")
                return

        # Validate and Parse Payload
        data = None
        if payload_input:
            try:
                data = json.loads(payload_input)
            except json.JSONDecodeError:
                QtWidgets.QMessageBox.critical(self, "Error", "Payload must be in valid JSON format.")
                return

        # Setup Authentication
        auth = None
        if auth_type == "Basic":
            username = self.username_entry.text().strip()
            password = self.password_entry.text().strip()
            if username and password:
                auth = (username, password)
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Username and Password are required for Basic Authentication.")
                return
        elif auth_type == "Bearer Token":
            token = self.token_entry.text().strip()
            if token:
                headers['Authorization'] = f"Bearer {token}"
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "Bearer Token is required for Bearer Token Authentication.")
                return

        # Perform the request in a separate thread
        thread = Thread(target=self.execute_request, args=(method, url, headers, data, auth))
        thread.start()

    def execute_request(self, method, url, headers, data, auth):
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                auth=auth,
                timeout=30
            )
            QtCore.QMetaObject.invokeMethod(self, "display_response", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(object, response))
        except Exception as e:
            QtCore.QMetaObject.invokeMethod(self, "display_error", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(str, str(e)))

    @QtCore.pyqtSlot(object)
    def display_response(self, response):
        try:
            response_json = response.json()
            formatted_response = json.dumps(response_json, indent=4)
            self.response_editor.page().runJavaScript(f"editor.setValue({json.dumps(formatted_response)})")
            self.populate_response_tree(response_json)
        except ValueError:
            self.response_editor.page().runJavaScript(f"editor.setValue({json.dumps(response.text)})")
            self.response_tree.clear()

    def populate_response_tree(self, response_data, parent_item=None):
        self.response_tree.clear()
        if parent_item is None:
            parent_item = self.response_tree

        def add_items(data, tree_item):
            if isinstance(data, dict):
                for key, value in data.items():
                    item = QTreeWidgetItem([key])
                    tree_item.addTopLevelItem(item) if tree_item is self.response_tree else tree_item.addChild(item)
                    add_items(value, item)
            elif isinstance(data, list):
                for index, value in enumerate(data):
                    item = QTreeWidgetItem([f"[{index}]"])
                    tree_item.addTopLevelItem(item) if tree_item is self.response_tree else tree_item.addChild(item)
                    add_items(value, item)
            else:
                item = QTreeWidgetItem([str(data)])
                tree_item.addChild(item)

        add_items(response_data, parent_item)

    def visualize_response(self):
        response_text = self.response_editor.page().runJavaScript("editor.getValue()", self.on_visualize_response)

    def on_visualize_response(self, response_text):
        try:
            response_data = json.loads(response_text)
            if isinstance(response_data, dict) and all(isinstance(value, (int, float)) for value in response_data.values()):
                keys = list(response_data.keys())
                values = list(response_data.values())

                plt.figure(figsize=(10, 6))
                plt.bar(keys, values)
                plt.xlabel('Keys')
                plt.ylabel('Values')
                plt.title('Response Data Visualization')
                plt.xticks(rotation=45)

                buf = BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img = Image.open(buf)
                img.save("response_visualization.png")

                pixmap = QtGui.QPixmap("response_visualization.png")
                self.response_visual_label.setPixmap(pixmap)
                buf.close()
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "The response data is not suitable for visualization.")
        except json.JSONDecodeError:
            QtWidgets.QMessageBox.critical(self, "Error", "Invalid JSON format in response.")

    @QtCore.pyqtSlot(str)
    def display_error(self, error_message):
        QtWidgets.QMessageBox.critical(self, "Error", error_message)

    def get_ace_editor_html(self, initial_content="{}"):\
        return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.12/ace.js"></script>
                <style>
                    html, body {{
                        height: 100%;
                        margin: 0;
                        background-color: #2d2d2d;
                    }}
                    #editor {{
                        position: absolute;
                        top: 0;
                        bottom: 0;
                        left: 0;
                        right: 0;
                    }}
                </style>
            </head>
            <body>
                <div id="editor" style="height: 100%; width: 100%;">{initial_content}</div>
                <script>
                    var editor = ace.edit("editor");
                    editor.session.setMode("ace/mode/json");
                    editor.setTheme("ace/theme/monokai");
                    editor.setOption("maxLines", 30);
                </script>
            </body>
            </html>
        """

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as file:
                return json.load(file)
        # Return default configuration if config file does not exist
        return {
            "templates": {
                "Create Incident": {
                    "short_description": "Short description of the incident",
                    "priority": "2",
                    "category": "network",
                    "subcategory": "WAN"
                },
                "Update Change Request": {
                    "change_id": "CHG1234567",
                    "description": "Updated description for change request",
                    "state": "in progress"
                }
            }
        }

    def save_config(self):
        config = {
            "url": self.url_entry.text().strip(),
            "method": self.method_combo.currentText(),
            "auth_type": self.auth_combo.currentText(),
            "username": self.username_entry.text().strip(),
            "password": self.password_entry.text().strip(),
            "token": self.token_entry.text().strip(),
        }
        # Retrieve headers and payload from Ace editors to save them
        self.headers_editor.page().runJavaScript("editor.getValue()", lambda headers: self.save_payload_to_config(config, headers, "headers"))
        self.payload_editor.page().runJavaScript("editor.getValue()", lambda payload: self.save_payload_to_config(config, payload, "payload"))

    def save_payload_to_config(self, config, content, content_type):
        config[content_type] = content
        with open(CONFIG_FILE, "w") as file:
            json.dump(config, file, indent=4)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = RestApiTester()
    window.show()
    app.exec()
