package com.terrafirm.orders;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.List;

@Controller
public class OrderController {

    private final JdbcTemplate jdbcTemplate;

    public OrderController(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @GetMapping("/")
    public String orders(Model model) {
        String serverAddr = jdbcTemplate.queryForObject(
                "SELECT inet_server_addr()::text AS server_name", String.class);

        List<OrderDetail> orderDetails = jdbcTemplate.query(
                "SELECT order_id, product_id, unit_price, quantity, discount FROM order_details",
                (rs, rowNum) -> new OrderDetail(
                        rs.getInt("order_id"),
                        rs.getInt("product_id"),
                        rs.getBigDecimal("unit_price"),
                        rs.getInt("quantity"),
                        rs.getDouble("discount")
                )
        );

        model.addAttribute("serverAddr", serverAddr);
        model.addAttribute("orderDetails", orderDetails);
        return "orders";
    }
}
