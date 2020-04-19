#!/bin/bash

# This file downloads local copies of the UI resources required to run.

mkdir ui/css
mkdir ui/js

wget -O ui/css/bootstrap.min.css https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css
wget -O ui/js/OrbitControls.js https://cdn.jsdelivr.net/npm/three@0.101.1/examples/js/controls/OrbitControls.js
wget -O ui/js/three.js https://cdn.jsdelivr.net/npm/three@0.101.1/build/three.min.js
wget -O ui/js/jquery-3.3.1.slim.min.js https://code.jquery.com/jquery-3.3.1.slim.min.js
wget -O ui/js/popper.min.js https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js
wget -O ui/js/bootstrap.min.js https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js
