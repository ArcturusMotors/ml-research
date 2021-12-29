"""
Download, transform and simulate various binary datasets.
"""

# Author: Georgios Douzas <gdouzas@icloud.com>
#         Joao Fonseca <jpfonseca@novaims.unl.pt>
# License: MIT

from re import sub
from collections import Counter
from itertools import product
from urllib.parse import urljoin
from string import ascii_lowercase
from zipfile import ZipFile
from io import BytesIO, StringIO

import requests
import numpy as np
import pandas as pd
from sklearn.utils import check_X_y
from imblearn.datasets import make_imbalance

from .base import Datasets, FETCH_URLS, RANDOM_STATE


class ImbalancedBinaryDatasets(Datasets):
    """Class to download, transform and save binary class imbalanced
    datasets."""

    MULTIPLICATION_FACTORS = [2, 3]

    @staticmethod
    def _calculate_ratio(multiplication_factor, y):
        """Calculate ratio based on IRs multiplication factor."""
        ratio = Counter(y).copy()
        ratio[1] = int(ratio[1] / multiplication_factor)
        return ratio

    def _make_imbalance(self, data, multiplication_factor):
        """Undersample the minority class."""
        X_columns = [col for col in data.columns if col != "target"]
        X, y = check_X_y(data.loc[:, X_columns], data.target)
        if multiplication_factor > 1.0:
            sampling_strategy = self._calculate_ratio(multiplication_factor, y)
            X, y = make_imbalance(
                X, y, sampling_strategy=sampling_strategy, random_state=RANDOM_STATE
            )
        data = pd.DataFrame(np.column_stack((X, y)))
        data.iloc[:, -1] = data.iloc[:, -1].astype(int)
        return data

    def download(self):
        """Download the datasets and append undersampled versions of them."""
        super(ImbalancedBinaryDatasets, self).download()
        undersampled_datasets = []
        for (name, data), factor in list(
            product(self.content_, self.MULTIPLICATION_FACTORS)
        ):
            ratio = self._calculate_ratio(factor, data.target)
            if ratio[1] >= 15:
                data = self._make_imbalance(data, factor)
                undersampled_datasets.append((f"{name} ({factor})", data))
        self.content_ += undersampled_datasets
        return self

    def fetch_breast_tissue(self):
        """Download and transform the Breast Tissue Data Set.
        The minority class is identified as the `car` and `fad`
        labels and the majority class as the rest of the labels.

        http://archive.ics.uci.edu/ml/datasets/breast+tissue
        """
        data = pd.read_excel(FETCH_URLS["breast_tissue"], sheet_name="Data")
        data = data.drop(columns="Case #").rename(columns={"Class": "target"})
        data["target"] = data["target"].isin(["car", "fad"]).astype(int)
        return data

    def fetch_ecoli(self):
        """Download and transform the Ecoli Data Set.
        The minority class is identified as the `pp` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/ecoli
        """
        data = pd.read_csv(FETCH_URLS["ecoli"], header=None, delim_whitespace=True)
        data = data.drop(columns=0).rename(columns={8: "target"})
        data["target"] = data["target"].isin(["pp"]).astype(int)
        return data

    def fetch_eucalyptus(self):
        """Download and transform the Eucalyptus Data Set.
        The minority class is identified as the `best` label
        and the majority class as the rest of the labels.

        https://www.openml.org/d/188
        """
        data = pd.read_csv(FETCH_URLS["eucalyptus"])
        data = data.iloc[:, -9:].rename(columns={"Utility": "target"})
        data = data[data != "?"].dropna()
        data["target"] = data["target"].isin(["best"]).astype(int)
        return data

    def fetch_glass(self):
        """Download and transform the Glass Identification Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/glass+identification
        """
        data = pd.read_csv(FETCH_URLS["glass"], header=None)
        data = data.drop(columns=0).rename(columns={10: "target"})
        data["target"] = data["target"].isin([1]).astype(int)
        return data

    def fetch_haberman(self):
        """Download and transform the Haberman's Survival Data Set.
        The minority class is identified as the `1` label
        and the majority class as the `0` label.

        https://archive.ics.uci.edu/ml/datasets/Haberman's+Survival
        """
        data = pd.read_csv(FETCH_URLS["haberman"], header=None)
        data.rename(columns={3: "target"}, inplace=True)
        data["target"] = data["target"].isin([2]).astype(int)
        return data

    def fetch_heart(self):
        """Download and transform the Heart Data Set.
        The minority class is identified as the `2` label
        and the majority class as the `1` label.

        http://archive.ics.uci.edu/ml/datasets/statlog+(heart)
        """
        data = pd.read_csv(FETCH_URLS["heart"], header=None, delim_whitespace=True)
        data.rename(columns={13: "target"}, inplace=True)
        data["target"] = data["target"].isin([2]).astype(int)
        return data

    def fetch_iris(self):
        """Download and transform the Iris Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/iris
        """
        data = pd.read_csv(FETCH_URLS["iris"], header=None)
        data.rename(columns={4: "target"}, inplace=True)
        data["target"] = data["target"].isin(["Iris-setosa"]).astype(int)
        return data

    def fetch_libras(self):
        """Download and transform the Libras Movement Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/Libras+Movement
        """
        data = pd.read_csv(FETCH_URLS["libras"], header=None)
        data.rename(columns={90: "target"}, inplace=True)
        data["target"] = data["target"].isin([1]).astype(int)
        return data

    def fetch_liver(self):
        """Download and transform the Liver Disorders Data Set.
        The minority class is identified as the `1` label
        and the majority class as the '2' label.

        https://archive.ics.uci.edu/ml/datasets/liver+disorders
        """
        data = pd.read_csv(FETCH_URLS["liver"], header=None)
        data.rename(columns={6: "target"}, inplace=True)
        data["target"] = data["target"].isin([1]).astype(int)
        return data

    def fetch_pima(self):
        """Download and transform the Pima Indians Diabetes Data Set.
        The minority class is identified as the `1` label
        and the majority class as the '0' label.

        https://www.kaggle.com/uciml/pima-indians-diabetes-database
        """
        data = pd.read_csv(FETCH_URLS["pima"], header=None, skiprows=9)
        data.rename(columns={8: "target"}, inplace=True)
        return data

    def fetch_vehicle(self):
        """Download and transform the Vehicle Silhouettes Data Set.
        The minority class is identified as the `1` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/Statlog+(Vehicle+Silhouettes)
        """
        data = pd.DataFrame()
        for letter in ascii_lowercase[0:9]:
            partial_data = pd.read_csv(
                urljoin(FETCH_URLS["vehicle"], "xa%s.dat" % letter),
                header=None,
                delim_whitespace=True,
            )
            partial_data = partial_data.rename(columns={18: "target"})
            partial_data["target"] = partial_data["target"].isin(["van"]).astype(int)
            data = data.append(partial_data)
        return data

    def fetch_wine(self):
        """Download and transform the Wine Data Set.
        The minority class is identified as the `2` label
        and the majority class as the rest of the labels.

        https://archive.ics.uci.edu/ml/datasets/wine
        """
        data = pd.read_csv(FETCH_URLS["wine"], header=None)
        data.rename(columns={0: "target"}, inplace=True)
        data["target"] = data["target"].isin([2]).astype(int)
        return data

    def fetch_new_thyroid_1(self):
        """Download and transform the Thyroid 1 Disease Data Set.
        The minority class is identified as the `positive`
        label and the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=145
        """
        zipped_data = requests.get(FETCH_URLS["new_thyroid_1"]).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data)).read("new-thyroid1.dat").decode("utf-8")
        )
        data = pd.read_csv(
            StringIO(sub(r"@.+\n+", "", unzipped_data)),
            header=None,
            sep=", ",
            engine="python",
        )
        data.rename(columns={5: "target"}, inplace=True)
        data["target"] = data["target"].isin(["positive"]).astype(int)
        return data

    def fetch_new_thyroid_2(self):
        """Download and transform the Thyroid 2 Disease Data Set.
        The minority class is identified as the `positive`
        label and the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=146
        """
        zipped_data = requests.get(FETCH_URLS["new_thyroid_2"]).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data)).read("newthyroid2.dat").decode("utf-8")
        )
        data = pd.read_csv(
            StringIO(sub(r"@.+\n+", "", unzipped_data)),
            header=None,
            sep=", ",
            engine="python",
        )
        data.rename(columns={5: "target"}, inplace=True)
        data["target"] = data["target"].isin(["positive"]).astype(int)
        return data

    def fetch_cleveland(self):
        """Download and transform the Heart Disease Cleveland Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=980
        """
        zipped_data = requests.get(FETCH_URLS["cleveland"]).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data)).read("cleveland-0_vs_4.dat").decode("utf-8")
        )
        data = pd.read_csv(StringIO(sub(r"@.+\n+", "", unzipped_data)), header=None)
        data.rename(columns={13: "target"}, inplace=True)
        data["target"] = data["target"].isin(["positive"]).astype(int)
        return data

    def fetch_dermatology(self):
        """Download and transform the Dermatology Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=1330
        """
        data = pd.read_csv(FETCH_URLS["dermatology"], header=None)
        data.rename(columns={34: "target"}, inplace=True)
        data.drop(columns=33, inplace=True)
        data["target"] = data["target"].isin(["positive"]).astype(int)
        return data

    def fetch_led(self):
        """Download and transform the LED Display Domain Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=998
        """
        zipped_data = requests.get(FETCH_URLS["led"]).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data))
            .read("led7digit-0-2-4-5-6-7-8-9_vs_1.dat")
            .decode("utf-8")
        )
        data = pd.read_csv(StringIO(sub(r"@.+\n+", "", unzipped_data)), header=None)
        data.rename(columns={7: "target"}, inplace=True)
        data["target"] = data["target"].isin(["positive"]).astype(int)
        return data

    def fetch_page_blocks_1_3(self):
        """Download and transform the Page Blocks 1-3 Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=124
        """
        zipped_data = requests.get(FETCH_URLS["page_blocks_1_3"]).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data))
            .read("page-blocks-1-3_vs_4.dat")
            .decode("utf-8")
        )
        data = pd.read_csv(StringIO(sub(r"@.+\n+", "", unzipped_data)), header=None)
        data.rename(columns={10: "target"}, inplace=True)
        data["target"] = data["target"].isin(["positive"]).astype(int)
        return data

    def fetch_vowel(self):
        """Download and transform the Vowel Recognition Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=127
        """
        zipped_data = requests.get(FETCH_URLS["vowel"]).content
        unzipped_data = ZipFile(BytesIO(zipped_data)).read("vowel0.dat").decode("utf-8")
        data = pd.read_csv(StringIO(sub(r"@.+\n+", "", unzipped_data)), header=None)
        data.rename(columns={13: "target"}, inplace=True)
        data["target"] = data["target"].isin([" positive"]).astype(int)
        return data

    def fetch_yeast_1(self):
        """Download and transform the Yeast 1 Data Set.
        The minority class is identified as the `positive` label and
        the majority class as the `negative` label.

        http://sci2s.ugr.es/keel/dataset.php?cod=153
        """
        zipped_data = requests.get(FETCH_URLS["yeast_1"]).content
        unzipped_data = ZipFile(BytesIO(zipped_data)).read("yeast1.dat").decode("utf-8")
        data = pd.read_csv(StringIO(sub(r"@.+\n+", "", unzipped_data)), header=None)
        data.rename(columns={8: "target"}, inplace=True)
        data["target"] = data["target"].isin([" positive"]).astype(int)
        return data


class BinaryDatasets(Datasets):
    """Class to download, transform and save binary class datasets."""

    def fetch_banknote_authentication(self):
        """Download and transform the Banknote Authentication Data Set.

        https://archive.ics.uci.edu/ml/datasets/banknote+authentication
        """
        data = pd.read_csv(FETCH_URLS["banknote_authentication"], header=None)
        data.rename(columns={4: "target"}, inplace=True)
        return data

    def fetch_arcene(self):
        """Download and transform the Arcene Data Set.

        https://archive.ics.uci.edu/ml/datasets/Arcene
        """
        url = FETCH_URLS["arcene"]
        data, labels = [], []
        for data_type in ("train", "valid"):
            data.append(
                pd.read_csv(
                    urljoin(url, f"ARCENE/arcene_{data_type}.data"),
                    header=None,
                    sep=" ",
                ).drop(columns=list(range(1998, 10001)))
            )
            labels.append(
                pd.read_csv(
                    urljoin(
                        url,
                        ("ARCENE/" if data_type == "train" else "")
                        + f"arcene_{data_type}.labels",
                    ),
                    header=None,
                ).rename(columns={0: "target"})
            )
        data = pd.concat(data, ignore_index=True)
        labels = pd.concat(labels, ignore_index=True)
        data = pd.concat([data, labels], axis=1)
        data["target"] = data["target"].isin([1]).astype(int)
        return data

    def fetch_audit(self):
        """Download and transform the Audit Data Set.

        https://archive.ics.uci.edu/ml/datasets/Audit+Data
        """
        zipped_data = requests.get(FETCH_URLS["audit"]).content
        unzipped_data = (
            ZipFile(BytesIO(zipped_data))
            .read("audit_data/audit_risk.csv")
            .decode("utf-8")
        )
        data = pd.read_csv(StringIO(sub(r"@.+\n+", "", unzipped_data)), engine="python")
        data = (
            data.drop(columns=["LOCATION_ID"])
            .rename(columns={"Risk": "target"})
            .dropna()
        )
        return data

    def fetch_spambase(self):
        """Download and transform the Spambase Data Set.

        https://archive.ics.uci.edu/ml/datasets/Spambase
        """
        data = pd.read_csv(FETCH_URLS["spambase"], header=None)
        data.rename(columns={57: "target"}, inplace=True)
        return data

    def fetch_parkinsons(self):
        """Download and transform the Parkinsons Data Set.

        https://archive.ics.uci.edu/ml/datasets/parkinsons
        """
        data = pd.read_csv(FETCH_URLS["parkinsons"])
        data = pd.concat(
            [
                data.drop(columns=["name", "status"]),
                data[["status"]].rename(columns={"status": "target"}),
            ],
            axis=1,
        )
        data["target"] = data["target"].isin([0]).astype(int)
        return data

    def fetch_ionosphere(self):
        """Download and transform the Ionosphere Data Set.

        https://archive.ics.uci.edu/ml/datasets/ionosphere
        """
        data = pd.read_csv(FETCH_URLS["ionosphere"], header=None)
        data = data.drop(columns=[0, 1]).rename(columns={34: "target"})
        data["target"] = data["target"].isin(["b"]).astype(int)
        return data

    def fetch_breast_cancer(self):
        """Download and transform the Breast Cancer Wisconsin Data Set.

        https://archive.ics.uci.edu/ml/datasets/Breast+Cancer+Wisconsin+(Diagnostic)
        """
        data = pd.read_csv(FETCH_URLS["breast_cancer"], header=None)
        data = pd.concat(
            [data.drop(columns=[0, 1]), data[[1]].rename(columns={1: "target"})], axis=1
        )
        data["target"] = data["target"].isin(["M"]).astype(int)
        return data
