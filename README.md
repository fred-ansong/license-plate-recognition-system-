# License Plate Recognition System

## Overview
This project is a Python-based system that simulates license plate recognition for Amber Alert use cases. It scans traffic camera feeds, compares detected plates against alert databases, and flags matches with time and location metadata. A GUI built with Tkinter is used to present matched data.

## Features
- Optical Character Recognition (OCR) for plate detection
- Privacy-first: only stores data on matches
- GUI using Tkinter to view flagged vehicles
- Python-based, using OpenCV and pytesseract

## Technologies
- Python
- Tkinter
- OpenCV
- pytesseract
- Raspberry Pi (simulated camera input)

## How It Works
1. Scans a folder of simulated traffic camera images
2. Extracts license plate numbers using OCR
3. Cross-references against a list of flagged plates
4. Displays matches in a live GUI interface
5. Outputs location metadata for law enforcement

## Getting Started
Clone the repository and install dependencies:

```bash
pip install opencv-python pytesseract
