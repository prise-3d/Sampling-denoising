# main imports
import os, sys
import argparse
import numpy as np
import pandas as pd
import json

# keras imports
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.callbacks import ModelCheckpoint

from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


# other params
output_backup         = 'models/backups'
output_models         = 'models/saved'
output_data_file_name = 'pixels_data.csv'


'''
Coefficients of determination function for Keras model
'''
def coeff_determination(y_true, y_pred):
    SS_res =  K.sum(K.square( y_true-y_pred ))
    SS_tot = K.sum(K.square( y_true - K.mean(y_true) ) )
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )


'''
Create model structure (here only fully connected layers)
'''
def create_model(input_shape, weights_file=None):
    
    model = Sequential()
    model.add(Dense(64, activation='relu', input_dim=input_shape))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(2048, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(1024, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(128, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(16, activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(3, activation='relu'))

     # reload weights if exists
    if weights_file is not None:
        model.load_weights(weights_file)

    model.compile(loss='mean_squared_error', 
                    optimizer='adam', 
                    metrics=[coeff_determination])

    return model


def main():

    parser = argparse.ArgumentParser(description="Output data file")

    parser.add_argument('--folder', type=str, help="folder scenes pixels data")
    parser.add_argument('--output', type=str, help='output folder where pxels scenes data will be saved')
    parser.add_argument('--batch_size', type=int, help='batch size used as model input', default=32)
    parser.add_argument('--epochs', type=int, help='number of epochs used for training model', default=30)

    args = parser.parse_args()

    p_folder     = args.folder
    p_output     = args.output
    p_batch_size = args.batch_size
    p_epochs     = args.epochs
    
    # default params
    initial_epoch = 0

    scenes_list = os.listdir(p_folder)

    dataframes = []
    for scene in scenes_list:

        scene_path = os.path.join(p_folder, scene)
        datafile_path = os.path.join(scene_path, output_data_file_name)

        # if path exist
        if os.path.exists(datafile_path):

            df = pd.read_csv(datafile_path, sep=';', header=None)
            dataframes.append(df)

    data = pd.concat(dataframes)

    y_data = data.iloc[:, :3]
    x_data = data.iloc[:, 3:]

    y_train, y_test = train_test_split(y_data, test_size=0.9)
    x_train, x_test = train_test_split(x_data, test_size=0.9)


    # Restore model if exists
    # create backup folder for current model
    model_backup_folder = os.path.join(output_backup, p_output)
    if not os.path.exists(model_backup_folder):
        os.makedirs(model_backup_folder)

    # add of callback models
    filepath = os.path.join(output_backup, p_output, p_output + "-{loss:02f}-{val_loss:02f}__{epoch:02d}.hdf5")
    checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_best_only=True, mode='max')
    callbacks_list = [checkpoint]

    
    # check if backup already exists
    weights_filepath = None
    backups = sorted(os.listdir(model_backup_folder))

    if len(backups) > 0:

        # retrieve last backup epoch of model 
        last_model_backup = None
        max_last_epoch = 0

        for backup in backups:

            last_epoch = int(backup.split('__')[1].replace('.hdf5', ''))

            if last_epoch > max_last_epoch and last_epoch < p_epochs:
                max_last_epoch = last_epoch
                last_model_backup = backup

        if last_model_backup is None:
            print("Epochs asked is already computer. Noee")
            sys.exit(1)

        initial_epoch = max_last_epoch
        print("-------------------------------------------------")
        print("Previous backup model found",  last_model_backup, "with already", initial_epoch, "done...")
        print("Resuming from epoch", str(initial_epoch + 1))
        print("-------------------------------------------------")

        # load weights
        weights_filepath = os.path.join(model_backup_folder, last_model_backup)

    # create model with number of columns
    model = create_model(x_train.shape[1], weights_filepath)

    model.summary()

    # Train the model, iterating on the data in batches of 32 samples
    model.fit(x_train, y_train, validation_split=0.3, initial_epoch=initial_epoch, epochs=p_epochs, batch_size=p_batch_size, callbacks=callbacks_list)


    # save the model into HDF5 file
    model_output_path = os.path.join(output_models, p_output + '.json')
    json_model_content = model.to_json()

    with open(model_output_path, 'w') as f:
        print("Model saved into ", model_output_path)
        json.dump(json_model_content, f, indent=4)

    model.save_weights(model_output_path.replace('.json', '.h5'))

if __name__ == "__main__":
    main()