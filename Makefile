# ---------------- Install the project ---------------- #
install:
	@echo "Installing the projec"
	@echo "Creating virtual environment"
	@python3 -m venv claritycare-env
	@echo "-> OK"
	@echo "Activating virtual environment"
	@. claritycare-env/bin/activate
	@echo "-> OK"
	@echo "Upgrading pip"
	@claritycare-env/bin/pip install --upgrade pip
	@echo "Installing requirements"
	@claritycare-env/bin/pip install --no-deps -r requirements.txt
	@echo "-> OK"
	@echo "Project installed!"

### ---------------   Lint  --------------- ###

pylint:
	claritycare-env/bin/python -m pylint --rcfile=pylint.conf src

lint:
	make pylint


