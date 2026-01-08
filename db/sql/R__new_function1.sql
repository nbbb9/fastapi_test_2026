CREATE OR REPLACE FUNCTION new_fuction()
    RETURNS json
    LANGUAGE plpgsql
AS
$$
    DECLARE
        postData JSON;
    BEGIN
        SELECT to_json(p)
        INTO postData
        FROM posts p
        WHERE p.username = '새로운 Function 생성'
        LIMIT 1;

        -- 새로운 주석을 추가해봅니다.

        RETURN postData;
    END;
$$;