# Fair Allocation Algorithms - Demo Website
This repository contains the source code for a demo website showcasing the implementation of five fair allocation algorithms that were added to an open-source Python library - Fairpyx as part of final project for a Computer Science degree.

## to the website
to try it yourself go to <a href="https://tome.csariel.xyz/">https://tome.csariel.xyz/<a>

## Overview
This project demonstrates the functionality of five new fair allocation algorithms that were added to an existing open-source Python library- Fairpyx.  
The website provides an interactive interface where users can input their data, run the algorithms, and view the results.

## Algorithms
The following algorithms were implemented as part of this project:
  * TTC (Top Trading-Cycle): Assigns one course in each round to each student, the winning students are defined based on the students’ bid values.
  * SP (Second Price): In each round distributes one course to each student, with the refund of the bids according to the price of the course.
  * TTC-O: Assigns one course in each round to each student, the winning students are defined based on the students’ bid values. Uses linear planning for optimality.
  * SP-O: In each round distributes one course to each student, with the refund of the bids according to the price of the course. Uses linear planning for optimality.
  * OC (Ordinal-then-Cardinal): In the OC algorithm for CAP, we maximize ordinal utility followed by maximizing cardinal utility among rank-maximal solutions, performing this two-part optimization once for the whole market.

Each algorithm addresses different aspects of fair allocation, providing users with a variety of methods to solve allocation problems.

## Technologies Used
  Frontend: HTML, CSS, JavaScript  
  Backend: Flask, Python

## Contributors
  * <a href="https://github.com/MoriyaEster">Moriya Ester  Ohayon<a>
  * <a href="https://github.com/TamarBarIlan">Tamar Bar-Ilan<a>
  * <a href="https://github.com/ofekats">Ofek Kats<a>
  
