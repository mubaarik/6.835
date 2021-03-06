import keras
from keras.layers import Input, Dense, Dropout, Flatten, Conv2D, MaxPooling2D, AveragePooling2D
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
import numpy as np

num_classes = 7 #angry, disgust, fear, happy, sad, surprise, neutral
batch_size = 256
epochs = 5

# READ IN KAGGLE DATA
with open("data/kaggle_fer2013/fer2013.csv") as file:
     data = file.readlines()

lines = np.array(data)

x_train, y_train, x_test, y_test = [], [], [], []

# 1. A) SPLIT DATA INTO TEST AND TRAIN
for i in range(1,lines.size):
    emotion, img, usage = lines[i].split(",")
    val = img.split(" ")
    pixels = np.array(val, 'float32')
    emotion = keras.utils.to_categorical(emotion, num_classes)

    if 'Training' in usage:
        y_train.append(emotion)
        x_train.append(pixels)
    elif 'PublicTest' in usage:
        y_test.append(emotion)
        x_test.append(pixels)

print(len(x_train))
print(x_train[0])
print(len(y_train))

# 1. B) CAST AND NORMALIZE DATA
x_train = np.array(x_train).astype(np.float32)
x_test = np.array(x_test).astype(np.float32)
max_val = np.amax(x_train);
x_train = x_train/max_val
x_test = x_test/max_val
# 1. C) RESHAPE DATA
x_train = x_train.reshape(x_train.shape[0],48,48,1);
x_test = x_test.reshape(x_test.shape[0],48,48,1);


#train_data = np.column_stack((x_train,y_train))
#test_data = np.column_stack((x_test,y_test))

## Simple Model
# 2. CREATE CNN MODEL
def cnn_model_one(num_filters=64,filter_size =(5,5), epochs=5,pool_size=(5,5),batch_size=256,stride=2,filename='model_1.h5'):
  input_layer = Input(shape=(48, 48, 1, ));
  conv_layer = Conv2D(num_filters,filter_size,activation='relu')(input_layer);
  pool_layer = MaxPooling2D(pool_size=pool_size, strides=(2,2))(conv_layer);
  flatten_layer = Flatten()(pool_layer);
  dense_1 = Dense(1024,activation='relu')(flatten_layer);
  dense_2 = Dense(7,activation='softmax')(dense_1);
  # 3. A) DATA BATCH PROCESS
  _batch_size = 256;
  data_gen = ImageDataGenerator().flow(x_train, y_train, batch_size=_batch_size);
  # 3. B) TRAIN AND SAVE MODEL
  model = Model(inputs=input_layer, outputs=dense_2)
  model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy']);
  model.fit_generator(data_gen,steps_per_epoch=len(x_train)/_batch_size, epochs=epochs);
  model.save(filename);
def cnn_model_two(num_filters=64,filter_size =(5,5), epochs=45,pool_size=(5,5),batch_size=256,stride=2,filename="model_1.h5"):
  input_layer = Input(shape=(48, 48, 1, ));
  conv_layer = Conv2D(num_filters,filter_size,activation='relu')(input_layer);
  pool_layer = MaxPooling2D(pool_size=pool_size, strides=(stride,stride))(conv_layer);
  drop = Dropout(.2)(pool_layer);
  conv_layer2 = Conv2D(num_filters,filter_size,activation='relu')(drop);
  pool_layer = MaxPooling2D(pool_size=pool_size, strides=(stride,stride))(conv_layer2);
  flatten_layer = Flatten()(pool_layer);
  dense_1 = Dense(1024,activation='relu')(flatten_layer);
  dense_2 = Dense(7,activation='softmax')(dense_1);
  # 3. A) DATA BATCH PROCESS
  data_gen = ImageDataGenerator(rotation_range=10).flow(x_train, y_train, batch_size=batch_size);
  # 3. B) TRAIN AND SAVE MODEL
  model = Model(inputs=input_layer, outputs=dense_2)
  model.compile(loss='categorical_crossentropy',
                optimizer='adam',
                metrics=['accuracy']);
  model.fit_generator(data_gen,steps_per_epoch=len(x_train)/batch_size, epochs=epochs);
  model.save(filename)
cnn_model_two(filename='model_2.h5')
def scorer(filename='model_2.h5'):
  from keras.models import Model, load_model
  model = load_model(filename);
  train_score = model.evaluate(x_train,np.array(y_train));
  test_score = model.evaluate(x_test,np.array(y_test));
  print("training score",train_score);
  print("test_score",test_score);
scorer()

