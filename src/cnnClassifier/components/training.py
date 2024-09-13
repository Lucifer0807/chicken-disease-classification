import os
import urllib.request as request
from zipfile import ZipFile
import tensorflow as tf
from src.cnnClassifier.entity.config_entity import (DataIngestionConfig,
                                                    PrepareBaseModelConfig,
                                                    PrepareCallbacksConfig,
                                                    TrainingConfig)
import time
from pathlib import Path


class Training:
    def __init__(self, config: TrainingConfig):
        self.config = config

    def get_base_model(self):
        # Load the updated base model
        self.model = tf.keras.models.load_model(
            self.config.updated_base_model_path
        )

        # Recompile the model with a new optimizer
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(),  # You can specify any optimizer you prefer
            loss='categorical_crossentropy',  # Replace with your appropriate loss function
            metrics=['accuracy']  # Replace with your desired metrics
        )

    def train_valid_generator(self):
        # Define arguments for the data generator
        datagenerator_kwargs = dict(
            rescale=1. / 255,
            validation_split=0.20
        )

        dataflow_kwargs = dict(
            target_size=self.config.params_image_size[:-1],
            batch_size=self.config.params_batch_size,
            interpolation="bilinear"
        )

        # Create a validation data generator
        valid_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(
            **datagenerator_kwargs
        )

        self.valid_generator = valid_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="validation",
            shuffle=False,
            **dataflow_kwargs
        )

        # Create a training data generator with augmentation if needed
        if self.config.params_is_augmentation:
            train_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(
                rotation_range=40,
                horizontal_flip=True,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                **datagenerator_kwargs
            )
        else:
            train_datagenerator = valid_datagenerator

        self.train_generator = train_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="training",
            shuffle=True,
            **dataflow_kwargs
        )

    @staticmethod
    def save_model(path: Path, model: tf.keras.Model):
        # Automatically detect format based on file extension
        model.save(str(path))

    def train(self, callback_list: list):
        self.steps_per_epoch = self.train_generator.samples // self.train_generator.batch_size
        self.validation_steps = self.valid_generator.samples // self.valid_generator.batch_size

        # Train the model
        self.model.fit(
            self.train_generator,
            epochs=self.config.params_epochs,
            steps_per_epoch=self.steps_per_epoch,
            validation_steps=self.validation_steps,
            validation_data=self.valid_generator,
            callbacks=callback_list
        )

        # Save the model in .keras format
        self.save_model(
            path=self.config.trained_model_path.with_suffix('.keras'),  # Update the file extension to .keras
            model=self.model
        )
