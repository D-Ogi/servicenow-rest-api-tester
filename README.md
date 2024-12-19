
# ServiceNow REST API Tester

A PyQt6-based graphical user interface for testing REST API endpoints, with a focus on ServiceNow APIs. This tool simplifies the process of building requests (including headers, payload, and authentication), sending requests, viewing responses in both raw and structured tree formats, and visualizing numeric response data.

## Features

- **GUI-based**: No need to manage cURL commands or raw JSON files—interact through a clean PyQt6 interface.
- **Multiple HTTP Methods**: Support for GET, POST, PUT, DELETE, PATCH, OPTIONS, and HEAD.
- **Authentication Options**: Supports Basic and Bearer Token authentication.
- **JSON Editors**: Built-in ACE editor for headers and payload, with formatting and template insertion.
- **Tree View**: Visualize response payload structures in a hierarchical tree.
- **Visualization**: Basic bar chart generation from numeric JSON responses using `matplotlib`.

## Screenshot

<img width="938" alt="image" src="https://github.com/user-attachments/assets/5dfdb9af-1233-424c-bf1a-89e5a364c78a" />


## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/D-Ogi/servicenow-rest-api-tester.git
   ```

2. **Install Python dependencies:**
   ```bash
   cd servicenow-rest-api-tester
   pip install matplotlib requests PyQt6 PyQt6-WebEngine Pillow
   ```

3. **Run the Application:**
   ```bash
   python api.py
   ```

## Configuration

- **config.json**:  
  The application loads and saves configuration details here.  
  - `url`: Default API endpoint URL.  
  - `method`: Default HTTP method.  
  - `auth_type`: Default authentication type.  
  - `username`, `password`: For Basic Auth.  
  - `token`: For Bearer Token Auth.  
  - `headers`: Default headers as JSON.  
  - `payload`: Default request payload as JSON.  
  - `templates`: JSON templates for payload insertion.

## Usage

1. Launch the application.
2. Enter the endpoint URL and select the HTTP method.
3. Choose authentication type and provide credentials if necessary.
4. Edit headers and payload in the ACE editor.
5. Click "Send Request" to execute the request.
6. View raw response or navigate through the JSON structure in the tree view.
7. If applicable, visualize numeric data by switching to the "Visualization" tab.

## Templates

Load predefined templates for common API payloads (e.g., for creating incidents or updating change requests in ServiceNow). This feature can speed up testing by inserting ready-to-use JSON structures.


# Changelog

All notable changes to this project will be documented in this file.

## 2024-12-19

- Initial setup of repository
