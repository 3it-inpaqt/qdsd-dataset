from pathlib import Path

import labelbox as lb

from settings import settings


##--------------------------##

class Label():

    def clear_dataset(self, dataset):
        """
        Remove all the data of a dataset

        :param dataset: Name of the dataset
        :return: Remove all the data of a dataset
        """
        for data_row in dataset.data_rows():
            data_row.delete()
        return

    def delete_dataset(self, dataset):
        """
        Delete a dataset

        :param dataset: Name of the dataset
        :return: delete a dataset
        """
        for data_row in dataset.data_rows():
            data_row.delete()
        dataset.delete()
        return

    def get_data_row_link(self, ID, dataset):
        """
        Extract the link of the data in the dataset

        :param ID: the ID of the desired data_row link
        :param dataset: the dataset of the ID
        :return: data_row link of the ID, if multiple corresponding ID, return a list of link
        """

        for data_row in dataset.data_rows():
            if data_row.external_id == ID:
                ID_d = data_row.row_data
        if not ID_d:
            print("Error no ID found")
            return
        else:
            return ID_d

    def attachement_layer(self, file_path: Path, file_basename: str, data_row):
        """
        Attached a layer on a data

        :file_path: The path where to save the image
        :file_basename: File name
        :param data_row: the image in LabelBox
        :return: attached 2 layers on the image (raw, dy/dx, dx/dy)

        """

        # Creation of a tmp dataset

        dataset_tmp = self.client.create_dataset(name='Dataset_tmp',
                                                 description='Dataset tmp create to add layer in a define dataset')

        # Attachement for the derivate in X

        datarow_tmp = dataset_tmp.create_data_row(external_id=file_basename + '_DyDx.png',
                                                  row_data=file_path + '/DyDx/' + file_basename + '_DyDx.png')
        datarow_link = self.get_data_row_link(file_basename + '_DyDx.png', dataset_tmp)
        data_row.create_attachment(attachment_type="IMAGE_OVERLAY", attachment_value=datarow_link,
                                   attachment_name="DxDy")

        # Attachement for the derivate in Y

        datarow_tmp = dataset_tmp.create_data_row(external_id=file_basename + '_DxDy.png',
                                                  row_data=file_path + '/DxDy/' + file_basename + '_DxDy.png')
        datarow_link = self.get_data_row_link(file_basename + '_DxDy.png', dataset_tmp)
        data_row.create_attachment(attachment_type="IMAGE_OVERLAY", attachment_value=datarow_link,
                                   attachment_name="DxDy")

        self.delete_dataset(dataset_tmp)
        return

    def load_img_into_labelbox(self, file_path: str, file_basename: str):
        """
        Upload a image with 2 attachement in Labelbox

        :param out_img_file:
        :param file_basename:
        return: Upload a image with 2 attachement in Labelbox
        """

        self.__int__()

        if not settings.dataset_link:
            if not settings.dataset_name:
                dataset = self.client.create_dataset(name='Default')
                settings.dataset_name = 'Default'
            else:
                dataset = self.client.get_datasets(where=lb.Dataset.name == settings.dataset_name).get_one()
                if dataset == None:
                    dataset = self.client.create_dataset(name=settings.dataset_name)
        else:
            dataset = self.client.get_dataset(settings.dataset_link)

        print(f'Upload {file_basename} in {dataset.name}')

        # Check if the image is already upload
        for data_row in dataset.data_rows():
            ID = data_row.external_id
            if ID.startswith(file_basename):
                print(f'Image {file_basename} is already upload')
                return

        data_row = dataset.create_data_row(external_id=file_basename + '.png',
                                           row_data=file_path + '/raw/' + file_basename + '.png')

        self.attachement_layer(file_path, file_basename, data_row)

        return

    def __int__(self):

        Key = settings.API_KEY
        self.client = lb.Client(api_key=Key)

        return


label = Label()
