import numpy as np
from tensorflow import keras
from keras._tf_keras.keras.preprocessing.image import load_img, img_to_array
from keras._tf_keras.keras.models import load_model
import os


class PredictionPipeline:
    def __init__(self, filename):
        self.filename = filename

    def predict(self):
        # Load the model
        model_path = os.path.join("artifacts", "training", "model.keras")
        model = load_model(model_path)

        # Preprocess the image
        imagename = self.filename
        test_image = load_img(imagename, target_size=(224, 224))  # load the image
        test_image = img_to_array(test_image)  # convert to numpy array
        test_image = np.expand_dims(test_image, axis=0)  # add batch dimension
        test_image = test_image / 255.0  # normalize pixel values if needed

        # Make prediction
        result = np.argmax(model.predict(test_image), axis=1)

        # Interpret the result
        if result[0] == 1:
            prediction = 'Healthy'
            return ["The chicken is healthy"]
        else:
            prediction = 'Coccidiosis'
            return ["The chicken is having coccidiosis"]

        return [{"image": prediction}]

# Usage Example
# pipeline = PredictionPipeline(filename="path_to_image.jpg")
# print(pipeline.predict())
