install pyenv-virtualenvgit clone https://github.com/pyenv/pyenv-virtualenvwrapper.git $(pyenv root)/plugins/pyenv-virtualenvwrapper# Setting up the python dev environment on macOS

Using virtual environments and getting package imports to work

## Clone the project
Use git to clone the project to your local workspace `<path_to_your_project_workspace>` 


## Set up a python virtual environment for this project
Install the python virtual environment manager  
`brew install pyenv-virtualenv`  

Enable auto-activation in your terminal shell profile  
`echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bash_profile`  
`source ~/.bash_profile`  

Create the virtual environment  
`pyenv virtualenv netdata-venv`

Install the Python Environment Manager extension for VSCode (by Don Jayamanne)

## Add the netdata core python modules into the PYTHONPATH for this virtual environment
Install the virtual environment wrapper tool  
`brew install pyenv-virtualenvwrapper`  

Open a terminal session for the `netdata-venv` environment using the Python Environment Manager extension or ...  

`pyenv shell netdata-venv` 

Initialise the wrapper tool  
`pyenv virtualenvwrapper_lazy`  

Add the netdata core python modules directory to the PYTHONPATH env variable  
`add2virtualenv <path_to_your_project_workspace>/netdata/collectors/python.d.plugin/python_modules`


## Install postgresql package for the mock database
`pip install psycopg`

## Install ibm_db package for the real IBM i database
`pip install ibm_db`


