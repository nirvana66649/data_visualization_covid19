package com.gdut;

public class ProvinceCovidData {
    private final String province;
    private final Integer confirmed;
    private final Integer cured;
    private final Integer dead;

    public ProvinceCovidData(String province, Integer confirmed, Integer cured, Integer dead) {
        this.province = province;
        this.confirmed = confirmed;
        this.cured = cured;
        this.dead = dead;
    }

    public String getProvince() {
        return province;
    }

    public Integer getConfirmed() {
        return confirmed;
    }

    public Integer getCured() {
        return cured;
    }

    public Integer getDead() {
        return dead;
    }

    // 提供用于聚类的特征数组，处理 null 值
    public double[] getFeatures() {
        return new double[]{
                confirmed != null ? confirmed : 0.0,
                cured != null ? cured : 0.0,
                dead != null ? dead : 0.0
        };
    }
}
