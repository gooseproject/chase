What is chase?
--------------

Chase is the GoOSe Project reporting tool. It provides basic information from koji, github and other tools we use. Currently, it's functionality is to help report on packages, builds and other information from koji.

Using chase
-----------

$ chase -h

Dependencies
============

Skein will not function without the following dependencies.

* koji >= 1.6.0 (http://fedorahosted.org/koji)

Configuration
=============

To setup chase, you just need to install it:

$ sudo python setup.py install

Then give it a run

$ chase -h


