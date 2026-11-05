package com.smiota.common.entity;

import jakarta.persistence.*;
import java.io.Serializable;
import java.sql.Timestamp;
import java.util.Objects;

@Entity
@Table(name = "oauth2_code_grants")
public class Oauth2CodeGrantsEntity implements Serializable {
    private static final long serialVersionUID = 1L;

    @Id
    @Column(name = "code", length = 64)
    private String code;

    @Column(name = "client_id", length = 64)
    private String clientId;

    @Column(name = "code_expiration", nullable = false)
    private Timestamp codeExpiration;

    @Column(name = "scope", length = 128)
    private String scope;

    public Oauth2CodeGrantsEntity() {}

    public String getCode() {
        return this.code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getClientId() {
        return this.clientId;
    }

    public void setClientId(String clientId) {
        this.clientId = clientId;
    }

    public Timestamp getCodeExpiration() {
        return this.codeExpiration;
    }

    public void setCodeExpiration(Timestamp codeExpiration) {
        this.codeExpiration = codeExpiration;
    }

    public String getScope() {
        return this.scope;
    }

    public void setScope(String scope) {
        this.scope = scope;
    }

}
