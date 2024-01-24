# -*- coding: utf-8 -*-
"""edge.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hRSRqQTYMj8iePYJzXXfNx55crmlWdZL
"""

import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
r=cv.imread('a.jpg')
img = cv.imread('a.jpg', cv.IMREAD_GRAYSCALE)
assert img is not None, "file could not be read, check with os.path.exists()"
edges = cv.Canny(img,100,200)
plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
plt.show()

img = cv2.imread("a.jpg")
cImg = img.copy()
img = cv2.blur(img, (5, 5))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

scale = 1
delta = 0
ddepth = cv.CV_16S

grad_x = cv.Sobel(gray, ddepth, 1, 0, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)
grad_y = cv.Sobel(gray, ddepth, 0, 1, ksize=3, scale=scale, delta=delta, borderType=cv.BORDER_DEFAULT)

abs_grad_x = cv.convertScaleAbs(grad_x)
abs_grad_y = cv.convertScaleAbs(grad_y)

grad = cv.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
gradr=scale*1
gradg=scale*7
gradb=scale*6
ret, thresh = cv2.threshold(grad, 10, 255, cv2.THRESH_BINARY_INV)

c, h = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

areas = [cv2.contourArea(c1) for c1 in c]
maxAreaIndex = areas.index(max(areas))

cv2.drawContours(cImg, c, maxAreaIndex, (0, 0, 0), -1)
Nr=gradr/2
Ng=gradg/2
Nb=gradb/2

plt.imshow(cImg)
plt.show()

from PIL import Image
import numpy as np
from scipy.stats import mode

# Load the image
image_path = "/content/c3.jpg"  # Replace this with your image path
img = Image.open(image_path)

# Convert the image to a NumPy array for easier manipulation
img_array = np.array(img)

# Extract RGB channels
red_channel = img_array[:, :, 0].flatten()
green_channel = img_array[:, :, 1].flatten()
blue_channel = img_array[:, :, 2].flatten()

red_sum = np.sum(red_channel)
green_sum = np.sum(green_channel)
blue_sum = np.sum(blue_channel)

red_mean = np.mean(red_channel)*Nr
green_mean = np.mean(green_channel)*Ng
blue_mean = np.mean(blue_channel)*Nb

print("Average Red Value: ",red_mean)
print("Average Green Value: ",green_mean)
print("Average Blue Value: ",blue_mean)

import pandas as pd

# Replace 'your_dataset.xlsx' with the actual path to your Excel file
excel_path = 'BACKUP DATASET.xlsx'
df = pd.read_excel(excel_path)

# Display the first few rows of the DataFrame to ensure proper loading
print(df.head())
X = df[['Red_Mean', 'Green_Mean', 'Blue_Mean']]
y = df['Concentration']

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.svm import SVR

# Choose the appropriate kernel and parameters based on your dataset
svm_model = SVR(kernel='linear')  # You may experiment with other kernels like 'rbf', 'poly', etc.
svm_model.fit(X_train, y_train)

from sklearn.metrics import mean_squared_error, r2_score

# Make predictions on the test set
y_pred = svm_model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Squared Error: {mse}')
print(f'R-squared: {r2}')

new_input = np.array([red_mean, green_mean, blue_mean]).reshape(1, -1)
predicted_concentration = svm_model.predict(new_input)
print(f'Predicted Ore Concentration: {predicted_concentration[0]}')