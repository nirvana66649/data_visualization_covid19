package com.gdut;

import weka.clusterers.SimpleKMeans;
import weka.core.*;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

public class ProvinceClustering {

    public static void main(String[] args) {
        String inputCsv = "D:\\数据可视化\\数据\\20200210.csv";
        String outputCsv = "D:\\数据可视化\\数据\\20200210_clustered.csv";

        try {
            List<ProvinceCovidData> data = loadDataFromCSV(inputCsv);
            Instances wekaData = prepareWekaInstances(data);

            SimpleKMeans kMeans = new SimpleKMeans();
            kMeans.setOptions(new String[]{"-O"});
            kMeans.setNumClusters(5);
            kMeans.buildClusterer(wekaData);

            exportToCSV(data, kMeans, outputCsv);
            System.out.println("聚类完成，文件已保存至：" + outputCsv);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static List<ProvinceCovidData> loadDataFromCSV(String filepath) {
        List<ProvinceCovidData> list = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(filepath), StandardCharsets.UTF_8))) {
            String line;
            reader.readLine(); // 跳过标题行

            while ((line = reader.readLine()) != null) {
                String[] parts = line.split(",", -1);
                if (parts.length >= 4) {
                    String province = parts[0];
                    int confirmed = Integer.parseInt(parts[1]);
                    int cured = Integer.parseInt(parts[2]);
                    int dead = Integer.parseInt(parts[3]);

                    list.add(new ProvinceCovidData(province, confirmed, cured, dead));
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }

        return list;
    }

    private static Instances prepareWekaInstances(List<ProvinceCovidData> data) {
        ArrayList<Attribute> attributes = new ArrayList<>();
        attributes.add(new Attribute("confirmed"));
        attributes.add(new Attribute("cured"));
        attributes.add(new Attribute("dead"));

        Instances dataset = new Instances("CovidProvinceData", attributes, data.size());

        for (ProvinceCovidData d : data) {
            double[] features = d.getFeatures();
            Instance instance = new DenseInstance(3);
            instance.setValue(attributes.get(0), features[0]);
            instance.setValue(attributes.get(1), features[1]);
            instance.setValue(attributes.get(2), features[2]);
            dataset.add(instance);
        }

        dataset.setClassIndex(-1);
        return dataset;
    }

    private static void exportToCSV(List<ProvinceCovidData> data, SimpleKMeans kMeans, String outputFilePath) throws Exception {
        int[] assignments = kMeans.getAssignments();
        int[] clusterMap = remapClusterLabels(kMeans); // 重新映射聚类编号（风险排序）

        try (PrintWriter writer = new PrintWriter(new OutputStreamWriter(new FileOutputStream(outputFilePath), StandardCharsets.UTF_8))) {
            writer.println("Province,Cluster,Confirmed,Cured,Dead");

            for (int i = 0; i < data.size(); i++) {
                ProvinceCovidData d = data.get(i);
                int rawCluster = assignments[i];
                int mappedCluster = clusterMap[rawCluster];

                writer.printf("%s,%d,%d,%d,%d%n",
                        d.getProvince(),
                        mappedCluster,
                        d.getConfirmed(),
                        d.getCured(),
                        d.getDead());
            }
        }
    }

    // 按确诊数排序聚类编号，风险高的编号大
    private static int[] remapClusterLabels(SimpleKMeans kMeans) throws Exception {
        Instances centroids = kMeans.getClusterCentroids();
        int numClusters = centroids.numInstances();

        List<int[]> clusterRiskList = new ArrayList<>();
        for (int i = 0; i < numClusters; i++) {
            Instance centroid = centroids.instance(i);
            int confirmed = (int) centroid.value(0);
            clusterRiskList.add(new int[]{i, confirmed});
        }

        // 根据确诊数升序排序
        clusterRiskList.sort(Comparator.comparingInt(a -> a[1]));

        // old cluster id -> new cluster id (1 ~ k)
        int[] clusterMap = new int[numClusters];
        for (int newId = 0; newId < clusterRiskList.size(); newId++) {
            int oldId = clusterRiskList.get(newId)[0];
            clusterMap[oldId] = newId + 1;
        }

        return clusterMap;
    }
}
