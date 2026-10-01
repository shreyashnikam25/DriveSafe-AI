import os
import tensorflow as tf
from tensorflow.keras import layers, models

def train_drowsiness_model():
    print("Loading processed dataset...")
    
    IMG_SIZE = (64, 64)
    BATCH_SIZE = 64
    EPOCHS = 10

    train_dir = "data/processed/train"
    val_dir = "data/processed/val"

    if not os.path.exists(train_dir):
        print("Error: Processed dataset directory not found!")
        return

    # Load datasets in grayscale mode (matches IR night vision)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        color_mode="grayscale"
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        color_mode="grayscale"
    )

    # Optimize data loading pipeline for CPU
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    # Lightweight CNN Architecture for fast real-time inference
    model = models.Sequential([
        layers.Rescaling(1./255, input_shape=(64, 64, 1)),
        
        layers.Conv2D(32, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        
        layers.Flatten(),
        layers.Dropout(0.5),
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='sigmoid')  # 0 = Closed Eyes, 1 = Open Eyes
    ])

    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy']
    )

    model.summary()

    print("\nStarting CNN model training...")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS
    )

    # Save trained model weights
    os.makedirs("core/models", exist_ok=True)
    model.save("core/models/drowsiness_cnn.keras")
    print("\nTraining complete! Model saved to core/models/drowsiness_cnn.keras")

if __name__ == "__main__":
    train_drowsiness_model()