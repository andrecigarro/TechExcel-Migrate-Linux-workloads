package com.terrafirm.orders;

import java.math.BigDecimal;

public class OrderDetail {

    private final int orderId;
    private final int productId;
    private final BigDecimal unitPrice;
    private final int quantity;
    private final double discount;

    public OrderDetail(int orderId, int productId, BigDecimal unitPrice, int quantity, double discount) {
        this.orderId = orderId;
        this.productId = productId;
        this.unitPrice = unitPrice;
        this.quantity = quantity;
        this.discount = discount;
    }

    public int getOrderId() { return orderId; }
    public int getProductId() { return productId; }
    public BigDecimal getUnitPrice() { return unitPrice; }
    public int getQuantity() { return quantity; }
    public double getDiscount() { return discount; }
}
