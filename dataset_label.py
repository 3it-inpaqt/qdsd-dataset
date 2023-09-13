from pathlib import Path
from typing import Optional

from labelbox import AssetAttachment, Client, DataRow, Dataset

from settings import settings


class DatasetLabel(Client):

    def __int__(self):
        """
        Create a LabelBox client connected to a specific dataset.
        Use setting values to establish the connection.
        """
        super().__init__(api_key=settings.api_key)
        self._dataset: Dataset

        # If the dataset id is specified, use it
        if settings.dataset_id:
            self._dataset = self.get_dataset(settings.dataset_id)
        else:
            # If the dataset name is specified, try to find it
            if settings.dataset_name:
                self._dataset = self.get_datasets(where=Dataset.name == settings.dataset_name).get_one()
                if self._dataset is None:
                    # No link and the name is not found, create a new dataset
                    self._dataset = self.create_dataset(name=settings.dataset_name)
            else:
                raise ValueError("No dataset specified (id or name).")

    # def clear_dataset(self) -> None:
    #     """
    #     Remove every row of a dataset.
    #     """
    #     for data_row in self._dataset.data_rows():
    #         data_row.delete()
    #
    # def delete_dataset(self) -> None:
    #     """
    #     Clear and delete a dataset.
    #     """
    #     self.clear_dataset()
    #     self._dataset.delete()

    def get_data_row_link(self, row_id):
        """
        Extract the link of the data in the dataset.

        :param row_id: The ID of the desired data_row link.
        :return: The first row link that matches the id.
        """
        for data_row in self._dataset.data_rows():
            if data_row.external_id == row_id:
                return data_row.row_data

        raise ValueError(f"Data row '{row_id}' not found in dataset '{self._dataset.name}'.")

    def attachement_layers(self, file_path: Path, file_basename: str, data_row):
        """
        Attached a layer on a data

        :file_dir: The path where to save the image
        :file_basename: File name
        :param data_row: the image in LabelBox
        :return: attached 2 layers on the image (raw, dy/dx, dx/dy)

        """

        # FIXME: Try without creating a tmp dataset
        # Creation of a tmp dataset
        dataset_tmp = self.create_dataset(name='Dataset_tmp',
                                          description='Dataset tmp create to add layer in a define dataset')

        # Attachement for the derivative in Y
        dy_file = file_path / 'DzDy' / f'{file_basename}_DzDy.png'
        datarow_tmp = dataset_tmp.create_data_row(external_id=file_basename + '_DzDy.png',
                                                  row_data=file_path + '/DzDy/' + file_basename + '_DzDy.png')
        datarow_link = self.get_data_row_link(file_basename + '_DzDy.png', dataset_tmp)
        data_row.create_attachment(attachment_type="IMAGE_OVERLAY", attachment_value=datarow_link,
                                   attachment_name="DzDy")

        # Attachement for the derivate in X
        datarow_tmp = dataset_tmp.create_data_row(external_id=file_basename + '_DzDx.png',
                                                  row_data=file_path + '/DzDx/' + file_basename + '_DzDx.png')
        datarow_link = self.get_data_row_link(file_basename + '_DzDx.png', dataset_tmp)
        data_row.create_attachment(attachment_type="IMAGE_OVERLAY", attachment_value=datarow_link,
                                   attachment_name="DzDx")

    def load_img_into_labelbox(self, file_dir: Path, file_basename: str) -> Optional[DataRow]:
        """
        Upload an image with 2 attachement in Labelbox

        :param file_dir: The directory where the images are stored
        :param file_basename: The base name of the image to upload
        return: The data row reference of the uploaded image
        """
        print(f'Upload image "{file_basename}" in {self._dataset.name}')

        # Check if the image is already upload
        for data_row in self._dataset.data_rows():
            if data_row.external_id.startswith(file_basename):
                print(f'Image "{file_basename}" already exists in {self._dataset.name}')
                return None

        attachments = []
        for ax in ['DzDy', 'DzDx']:
            file = file_dir / f'{file_basename}_{ax}.png'
            if file.exists():
                attachments.append(AssetAttachment(self, {
                    'attachment_type': AssetAttachment.AttachmentType.IMAGE_OVERLAY,
                    'attachment_value': file,
                }))

        if len(attachments) == 0:
            print(f'No attachments found for image "{file_basename}".')

        return self._dataset.create_data_row(external_id=f'{file_basename}.png',
                                             row_data=file_dir / 'raw' / f'{file_basename}.png',
                                             attachments=attachments)
