#!/usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
#     Copyright (C) 2020  Consiglio Nazionale delle Ricerche                  #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epas-client",
    version="1.3.0",
    author="Team di ePAS - IIT/CNR",
    author_email="epas@iit.cnr.it",
    description="ePAS client per prelevamento timbratute da file " + 
        "locali/ftp/sftp e lettore badge Smartclock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/consiglionazionaledellericerche/epas-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=open('requirements.txt').readlines()
)
