/********************************************************************************
 * Copyright (c) 2018 - 2019 Contributors to the Eclipse Foundation
 * 
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 * 
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License v. 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0, or the W3C Software Notice and
 * Document License (2015-05-13) which is available at
 * https://www.w3.org/Consortium/Legal/2015/copyright-software-and-document.
 * 
 * SPDX-License-Identifier: EPL-2.0 OR W3C-20150513
 ********************************************************************************/

/**
 * HTTP client based on http
 */

import * as http from "http";
import * as https from "https";
import * as url from "url";

import { Subscription } from "rxjs/Subscription";

import * as TD from "@node-wot/td-tools";
// for Security definition
import * as WoT from "wot-typescript-definitions";

import { ProtocolClient, Content } from "@node-wot/core";
import { HttpForm, HttpHeader, HttpConfig } from "./http";

export default class HttpClient implements ProtocolClient {

  private readonly agent: http.Agent;
  private readonly provider: any;
  private proxyOptions: http.RequestOptions = null;
  private authorization: string = null;
  private authorizationHeader: string = "Authorization";
  private allowSelfSigned: boolean = false;

  constructor(config: HttpConfig = null, secure = false) {

    // config proxy by client side (not from TD)
    if (config!==null && config.proxy && config.proxy.href) {
      this.proxyOptions = this.uriToOptions(config.proxy.href, true);

      if (config.proxy.scheme === "basic") {
        if (!config.proxy.hasOwnProperty("username") || !config.proxy.hasOwnProperty("password")) console.warn(`HttpClient client configured for basic proxy auth, but no username/password given`);
        this.proxyOptions.headers = {};
        this.proxyOptions.headers['Proxy-Authorization'] = "Basic " + Buffer.from(config.proxy.username + ":" + config.proxy.password).toString('base64');
      } else if (config.proxy.scheme === "bearer") {
        if (!config.proxy.hasOwnProperty("token")) console.warn(`HttpClient client configured for bearer proxy auth, but no token given`);
        this.proxyOptions.headers = {};
        this.proxyOptions.headers['Proxy-Authorization'] = "Bearer " + config.proxy.token;
      }
      // security for hop to proxy
      if (this.proxyOptions.protocol === "https") {
        secure = true;
      }
      
      console.info(`HttpClient using ${secure ? "secure " : ""}proxy ${this.proxyOptions.hostname}:${this.proxyOptions.port}`);
    }

    // config certificate checks
    if (config!==null && config.allowSelfSigned!==undefined) {
      this.allowSelfSigned = config.allowSelfSigned;
      console.warn(`HttpClient allowing self-signed/untrusted certificates -- USE FOR TESTING ONLY`);
    }

    // using one client impl for both HTTP and HTTPS
    this.agent = secure ? new https.Agent() : new http.Agent();
    this.provider = secure ? https : http;
  }

  private getContentType(res: http.IncomingMessage): string {
    let header: string | string[] = res.headers['content-type']; // note: node http uses lower case here
    if (Array.isArray(header)) {
      // this should never be the case as only cookie headers are returned as array
      // but anyways...
      return (header.length > 0) ? header[0] : "";
    } else {
      return header;
    }
  }

  public toString(): string {
    return `[HttpClient]`;
  }

  public readResource(form: HttpForm): Promise<Content> {
    return new Promise<Content>((resolve, reject) => {

      let req = this.generateRequest(form, "GET");
      let info = <any>req;

      console.log(`HttpClient (readResource) sending ${info.method} to ${info.path}`);

      req.on("response", (res: http.IncomingMessage) => {
        console.log(`HttpClient received ${res.statusCode} from ${info.path}`);
        let contentType: string = this.getContentType(res);
        let body: Array<any> = [];
        res.on('data', (data) => { body.push(data) });
        res.on('end', () => {
          this.checkResponse(res.statusCode, contentType, Buffer.concat(body), resolve, reject);
        });
      });
      req.on("error", (err: any) => reject(err));
      req.end();
    });
  }

  public writeResource(form: HttpForm, content: Content): Promise<any> {
    return new Promise<void>((resolve, reject) => {

      let req = this.generateRequest(form, "PUT");
      let info = <any>req;

      req.setHeader("Content-Type", content.type);
      req.setHeader("Content-Length", content.body.byteLength);

      console.log(`HttpClient (writeResource) sending ${info.method} with '${req.getHeader("Content-Type")}' to ${info.path}`);

      req.on("response", (res: http.IncomingMessage) => {
        console.log(`HttpClient received ${res.statusCode} from ${info.path}`);
        let contentType: string = this.getContentType(res);
        //console.log(`HttpClient received headers: ${JSON.stringify(res.headers)}`);
        // Although 204 without payload is expected, data must be read 
        // to complete request (http blocks socket otherwise)
        // TODO might have response on write for future HATEOAS concept
        let body: Array<any> = [];
        res.on('data', (data) => { body.push(data) });
        res.on('end', () => {
          this.checkResponse(res.statusCode, contentType, Buffer.concat(body), resolve, reject);
        });
      });
      req.on('error', (err: any) => reject(err));
      req.write(content.body);
      console.debug("+++++++++++++++++++ REQUEST: "+req.getHeaders())
      req.end();
    });
  }

  public invokeResource(form: HttpForm, content?: Content): Promise<Content> {
    return new Promise<Content>((resolve, reject) => {

      let req = this.generateRequest(form, "POST");
      let info = <any>req;

      if (content) {
        req.setHeader("Content-Type", content.type);
        req.setHeader("Content-Length", content.body.byteLength);
      }

      console.log(`HttpClient (invokeResource) sending ${info.method} ${content ? "with '"+req.getHeader("Content-Type")+"' " : " "}to ${info.path}`);

      req.on("response", (res: http.IncomingMessage) => {
        console.log(`HttpClient received ${res.statusCode} from ${form.href}`);
        let contentType: string = this.getContentType(res);
        console.debug(`HttpClient received Content-Type: ${contentType}`);
        let body: Array<any> = [];
        res.on('data', (data) => { body.push(data) });
        res.on('end', () => {
          this.checkResponse(res.statusCode, contentType, Buffer.concat(body), resolve, reject);
        });
      });
      req.on("error", (err: any) => reject(err));
      if (content) {
        req.write(content.body);
      }
      req.end();
    });
  }

  public unlinkResource(form: HttpForm): Promise<any> {
    return new Promise<void>((resolve, reject) => {
      
      let req = this.generateRequest(form, "DELETE");
      let info = <any>req;

      console.log(`HttpClient (unlinkResource) sending ${info.method} to ${form.href}`);

      req.on("response", (res: http.IncomingMessage) => {
        console.log(`HttpClient received ${res.statusCode} from ${form.href}`);
        let contentType: string = this.getContentType(res);
        //console.log(`HttpClient received headers: ${JSON.stringify(res.headers)}`);
        // Although 204 without payload is expected, data must be read
        //  to complete request (http blocks socket otherwise)
        // TODO might have response on unlink for future HATEOAS concept
        let body: Array<any> = [];
        res.on('data', (data) => { body.push(data) });
        res.on('end', () => {
          this.checkResponse(res.statusCode, contentType, Buffer.concat(body), resolve, reject);
        });
      });
      req.on('error', (err: any) => reject(err));
      req.end();
    });
  }

  public subscribeResource(form: HttpForm, next: ((value: any) => void), error?: (error: any) => void, complete?: () => void): any {

    let active = true;
    let polling = () => {
      let req = this.generateRequest(form, "GET");
      let info = <any>req;
      
      // long timeout for long polling
      req.setTimeout(60*60*1000);

      console.log(`HttpClient (subscribeResource) sending ${info.method} to ${form.href}`);
  
      req.on("response", (res: http.IncomingMessage) => {
        console.log(`HttpClient received ${res.statusCode} from ${form.href}`);
        let contentType: string = this.getContentType(res);
        let body: Array<any> = [];
        res.on("data", (data) => { body.push(data) });
        res.on("end", () => {
          if (active) {
            this.checkResponse(
              res.statusCode,
              contentType,
              Buffer.concat(body),
              (data: any) => { 
                next(data);
                polling();
              },
              (err: any) => {
                if (error) error(err);
                if (complete) complete();
                active = false;
              }
            );
          }
        });
      });
      req.on("error", (err: any) => {
        if (error) error(err);
        if (complete) complete();
      });

      req.flushHeaders();
      req.end();
    };

    polling();

    return new Subscription( () => { active = false; } );
  }

  public start(): boolean {
    return true;
  }

  public stop(): boolean {
    if (this.agent && this.agent.destroy) this.agent.destroy();  // When running in browser mode, Agent.destroy() might not exist.
    return true;
  }

  public setSecurity(metadata: Array<TD.SecurityScheme>, credentials?: any): boolean {

    if (metadata === undefined || !Array.isArray(metadata) || metadata.length == 0) {
      console.warn(`HttpClient without security`);
      return false;
    }

    // TODO support for multiple security schemes
    let security: TD.SecurityScheme = metadata[0];

    if (security.scheme === "basic") {
      if (credentials === undefined || credentials.username === undefined || credentials.password === undefined) {
        throw new Error(`No Basic credentionals for Thing`);
      }
      this.authorization = "Basic " + Buffer.from(credentials.username + ":" + credentials.password).toString('base64');

    } else if (security.scheme === "bearer") {
      if (credentials === undefined || credentials.token === undefined) {
        throw new Error(`No Bearer credentionals for Thing`);
      }
      // TODO check security.in and adjust
      this.authorization = "Bearer " + credentials.token;

    } else if (security.scheme === "apikey") {
      let securityAPIKey : TD.APIKeySecurityScheme = <TD.APIKeySecurityScheme>security;
      if (credentials === undefined || credentials.apikey === undefined) {
        throw new Error(`No API key credentionals for Thing`);
      }
      this.authorization = credentials.apikey;
      if (securityAPIKey.in==="header" && securityAPIKey.name!==undefined) {
        this.authorizationHeader = securityAPIKey.name;
      }

    } else if (security.scheme === "nosec") {
      // nothing to do

    } else {
      console.error(`HttpClient cannot set security scheme '${security.scheme}'`);
      console.dir(metadata);
      return false;
    }

    if (security.proxy) {
      if (this.proxyOptions !== null) {
        console.info(`HttpClient overriding client-side proxy with security proxy '${security.proxy}`);
      }

      this.proxyOptions = this.uriToOptions(security.proxy, true);

      // TODO support for different credentials at proxy and server (e.g., credentials.username vs credentials.proxy.username)
      if (security.scheme == "basic") {
        if (credentials === undefined || credentials.username === undefined || credentials.password === undefined) {
          throw new Error(`No Basic credentionals for Thing`);
        }
        this.proxyOptions.headers = {};
        this.proxyOptions.headers['Proxy-Authorization'] = "Basic " + Buffer.from(credentials.username + ":" + credentials.password).toString('base64');
      } else if (security.scheme == "bearer") {
        if (credentials === undefined || credentials.token === undefined) {
          throw new Error(`No Bearer credentionals for Thing`);
        }
        this.proxyOptions.headers = {};
        this.proxyOptions.headers['Proxy-Authorization'] = "Bearer " + credentials.token;
      }
    }

    console.log(`HttpClient using security scheme '${security.scheme}'`);
    return true;
  }

  private uriToOptions(uri: string, ignoreProxy=false): https.RequestOptions {
    let requestUri = url.parse(uri);
    let options: https.RequestOptions = {};
    options.agent = this.agent;

    if (this.proxyOptions != null && ignoreProxy === false) {
      options.hostname = this.proxyOptions.hostname;
      options.port = this.proxyOptions.port;
      options.path = uri;
      options.headers = {};
      // copy header fields for Proxy-Auth etc.
      for (let hf in this.proxyOptions.headers) options.headers[hf] = this.proxyOptions.headers[hf];
      options.headers["Host"] = requestUri.hostname;

    } else {
      options.hostname = requestUri.hostname;
      // NodeJS cannot resolve localhost when not connected to any network...
      if (options.hostname==="localhost") {
        console.warn("LOCALHOST FIX");
        options.hostname = "127.0.0.1";
      }
      options.port = parseInt(requestUri.port, 10);
      options.path = requestUri.path;
      options.headers = {};
    }

    if (this.authorization !== null) {
      options.headers[this.authorizationHeader] = this.authorization;
    }

    if (this.allowSelfSigned === true) {
      options.rejectUnauthorized = false;
    }

    return options;
  }
  private generateRequest(form: HttpForm, dflt: string): http.ClientRequest {

    let options: http.RequestOptions = this.uriToOptions(form.href);

    options.method = dflt;

    if (typeof form["htv:methodName"] === "string") {
      console.log("HttpClient got Form 'methodName'", form["htv:methodName"]);
      switch (form["htv:methodName"]) {
        case "GET": options.method = "GET"; break;
        case "POST": options.method = "POST"; break;
        case "PUT": options.method = "PUT"; break;
        case "DELETE": options.method = "DELETE"; break;
        case "PATCH": options.method = "PATCH"; break;
        default: console.warn("HttpClient got invalid 'methodName', using default", options.method);
      }
    }

    let req = this.provider.request(options);

    console.debug(`HttpClient applying form`);
    //console.dir(form);

    // apply form data
    if (options.method === "GET" && typeof form.contentType === "string") {
      console.debug("HttpClient got Form 'contentType'", form.contentType);
      req.setHeader("Accept", form.contentType);
    }
    if (Array.isArray(form["htv:headers"])) {
      console.debug("HttpClient got Form 'headers'", form["htv:headers"]);
      let headers = form["htv:headers"] as Array<HttpHeader>;
      for (let option of headers) {
        req.setHeader(option["htv:fieldName"], option["htv:fieldValue"]);
      }
    } else if (typeof form["htv:headers"] === "object") {
      console.warn("HttpClient got Form SINGLE-ENTRY 'headers'", form["htv:headers"]);
      let option = form["htv:headers"] as HttpHeader;
      req.setHeader(option["htv:fieldName"], option["htv:fieldValue"]);
    }

    return req;
  }

  private checkResponse(statusCode: number, contentType: string, body: Buffer, resolve: Function, reject: Function) {
    if (statusCode < 200) {
      throw new Error(`HttpClient received ${statusCode} and cannot continue (not implemented, open GitHub Issue)`);
    } else if (statusCode < 300) {
      resolve({ type: contentType, body: body });
    } else if (statusCode < 400) {
      throw new Error(`HttpClient received ${statusCode} and cannot continue (not implemented, open GitHub Issue)`);
    } else if (statusCode < 500) {
      reject(new Error(`Client error: ${body.toString()}`));
    } else {
      reject(new Error(`Server error: ${body.toString()}`));
    }
  }
}
